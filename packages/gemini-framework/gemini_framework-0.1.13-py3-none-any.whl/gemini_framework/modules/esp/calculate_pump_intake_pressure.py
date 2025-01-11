from gemini_framework.abstract.unit_module_abstract import UnitModuleAbstract
from gemini_model.reservoir.inflow_performance import IPR
from gemini_model.well.pressure_drop import DPDT
from gemini_model.fluid.pvt_water_stp import PVTConstantSTP
from gemini_model.pump.esp import ESP
import numpy as np


class CalculatePumpIntakePressure(UnitModuleAbstract):

    def __init__(self, unit):
        super().__init__(unit)

        self.model = ESP()
        self.VLP = DPDT()
        self.IPR = IPR()

        self.link_input('measured', 'esp_flow')
        self.link_output('calculated', 'esp_intake_pressure')

    def step(self, loop):
        self.loop = loop
        self.loop.start_time = self.get_output_last_data_time('esp_intake_pressure')
        self.loop.compute_n_simulation()

        esp_unit = self.unit
        well_unit = self.unit.from_units[0]
        reservoir_unit = well_unit.from_units[0]

        time, result = self.get_input_data('esp_flow')
        well_flow = np.array(result)  # m3/hr

        pvt_param = dict()
        pvt_param['RHOL'] = reservoir_unit.parameters['liquid_density']
        pvt_param['VISL'] = reservoir_unit.parameters['liquid_viscosity']

        well_param = dict()
        well_param['soil_temperature'] = well_unit.parameters['productionwell_soil_temperature']

        well_traj = well_unit.parameters['productionwell_trajectory_table']
        length = []
        diameter = []
        angle = []
        roughness = []
        for ii in range(1, len(well_traj)):
            if well_traj[ii - 1]['MD'] >= esp_unit.parameters['esp_depth']:
                MD = well_traj[ii]['MD'] - well_traj[ii - 1]['MD']
                TVD = well_traj[ii]['TVD'] - well_traj[ii - 1]['TVD']

                length.append(MD)
                diameter.append(well_traj[ii]['ID'])
                angle.append(np.round(90 - np.arccos(TVD / MD) * 180 / np.pi, 2) * np.pi / 180)
                roughness.append(well_traj[ii]['roughness'])

        well_param['diameter'] = np.array(diameter)  # well diameter in [m]
        well_param['length'] = np.array(length)  # well depth in [m]
        well_param['angle'] = np.array(angle)  # well angle in [degree]
        well_param['roughness'] = roughness  # roughness of cells [m]
        well_param['friction_correlation'] = well_unit.parameters[
            'productionwell_friction_correlation']

        self.VLP.update_parameters(well_param)
        self.VLP.PVT = PVTConstantSTP()
        self.VLP.PVT.update_parameters(pvt_param)

        res_param = dict()
        res_param['reservoir_pressure'] = reservoir_unit.parameters['reservoir_pressure']
        res_param['reservoir_temperature'] = reservoir_unit.parameters['reservoir_temperature']
        res_param['productivity_index'] = well_unit.parameters['productionwell_productivity_index']
        res_param['type'] = 'production_reservoir'

        self.IPR.update_parameters(res_param)

        """Calculate bottomhole pressure from reservoir"""
        try:
            u = dict()
            x = []

            pbh_res = []
            for flow in well_flow:
                u['flow'] = flow

                self.IPR.calculate_output(u, x)

                # ASSERT
                y = self.IPR.get_output()
                pbh_res.append(y['pressure_bottomhole'])

        except Exception as e:
            print("ERROR:" + repr(e))
            pbh_res = None

        """Calculate pressure drop from bottomhole to ESP"""
        try:
            u = dict()
            x = []

            intake_pressure = []
            ii = 0
            for flow in well_flow:
                u['pressure'] = pbh_res[ii] * 1e5  # bar to Pa
                u['temperature'] = res_param['reservoir_temperature'] + 273.15  # C to K
                u['flowrate'] = flow / 3600  # m3/hr to m3/s
                u['temperature_ambient'] = float(
                    well_param['soil_temperature']) + 273.15  # C to K
                u['direction'] = 'up'

                self.VLP.calculate_output(u, x)

                # ASSERT
                y = self.VLP.get_output()

                intake_pressure.append(y['pressure_output'] / 1e5)  # Pa to bar
                ii = ii + 1

        except Exception as e:
            print("ERROR:" + repr(e))
            intake_pressure = None

        if intake_pressure:
            self.write_output_data('esp_intake_pressure', time, intake_pressure)
