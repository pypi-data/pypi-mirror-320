from gemini_framework.abstract.unit_module_abstract import UnitModuleAbstract
from gemini_model.well.pressure_drop import DPDT
from gemini_model.fluid.pvt_water_stp import PVTConstantSTP
from gemini_model.pump.esp import ESP
import numpy as np


class CalculatePumpDischargePressure(UnitModuleAbstract):

    def __init__(self, unit):
        super().__init__(unit)

        self.model = ESP()
        self.VLP1 = DPDT()

        self.link_input('measured', 'esp_flow')
        self.link_output('calculated', 'esp_discharge_pressure')

    def step(self, loop):
        self.loop = loop
        self.loop.start_time = self.get_output_last_data_time('esp_discharge_pressure')
        self.loop.compute_n_simulation()

        esp_unit = self.unit
        well_unit = self.unit.from_units[0]
        reservoir_unit = well_unit.from_units[0]

        # Get well data
        database = None
        for database in self.unit.plant.databases:
            if database.category == 'measured':
                break

        result, time = database.read_internal_database(
            self.unit.plant.name,
            well_unit.name,
            'productionwell_wellhead_pressure.measured',
            self.loop.start_time,
            self.loop.end_time,
            str(self.loop.timestep) + 's'
        )
        wellhead_pressure = np.array(result)
        time = np.array(time)

        result, time = database.read_internal_database(
            self.unit.plant.name,
            well_unit.name,
            'productionwell_wellhead_temperature.measured',
            self.loop.start_time,
            self.loop.end_time,
            str(self.loop.timestep) + 's'
        )
        wellhead_temperature = np.array(result)

        time, result = self.get_input_data('esp_flow')
        well_flow = np.array(result)  # m3/hr

        well_param = dict()
        well_param['soil_temperature'] = well_unit.parameters['productionwell_soil_temperature']

        well_param['diameter'] = np.array(
            [esp_unit.parameters['esp_tubing']])  # well diameter in [m]
        well_param['length'] = np.array(
            [esp_unit.parameters['esp_depth']])  # well depth in [m]
        well_param['angle'] = np.array([90 * np.pi / 180])  # well angle in [degree]
        well_traj = well_unit.parameters['productionwell_trajectory_table']
        well_param['roughness'] = np.array([well_traj[1]['roughness']])  # roughness of cells [m]
        well_param['friction_correlation'] = well_unit.parameters[
            'productionwell_friction_correlation']

        self.VLP1.update_parameters(well_param)

        pvt_param = dict()
        pvt_param['RHOL'] = reservoir_unit.parameters['liquid_density']
        pvt_param['VISL'] = reservoir_unit.parameters['liquid_viscosity']

        self.VLP1.PVT = PVTConstantSTP()
        self.VLP1.PVT.update_parameters(pvt_param)

        """Calculate discharge pressure via the pressure dop from wellhead to ESP"""
        u = dict()
        discharge_pressure = []
        for ii in range(1, self.loop.n_step):
            try:
                u['pressure'] = wellhead_pressure[ii] * 1e5  # bar to Pa
                u['temperature'] = wellhead_temperature[ii] + 273.15  # C to K
                u['flowrate'] = well_flow[ii] / 3600  # m3/hr to m3/s
                u['temperature_ambient'] = float(
                    well_param['soil_temperature']) + 273.15  # C to K
                u['direction'] = 'down'

                x = []
                self.VLP1.calculate_output(u, x)

                # ASSERT
                y = self.VLP1.get_output()

                discharge_pressure.append(y['pressure_output'] / 1e5)  # Pa to bar
            except Exception as e:
                self.logger.warn("ERROR:" + repr(e))
                discharge_pressure.append(None)

        if discharge_pressure:
            self.write_output_data('esp_discharge_pressure', time, discharge_pressure)
