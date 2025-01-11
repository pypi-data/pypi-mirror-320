from gemini_framework.abstract.unit_module_abstract import UnitModuleAbstract
from gemini_model.well.pressure_drop import DPDT
from gemini_model.fluid.pvt_water_stp import PVTConstantSTP
import numpy as np


class CalculateBottomholePressure(UnitModuleAbstract):

    def __init__(self, unit):
        super().__init__(unit)

        self.model = DPDT()

        self.link_input('measured', 'injectionwell_flow')
        self.link_input('measured', 'injectionwell_wellhead_pressure')
        self.link_input('measured', 'injectionwell_wellhead_temperature')
        self.link_output('calculated', 'injectionwell_bottomhole_pressure')

    def step(self, loop):
        self.loop = loop
        self.loop.start_time = self.get_output_last_data_time('injectionwell_bottomhole_pressure')
        self.loop.compute_n_simulation()

        well_param = dict()
        well_traj = self.unit.parameters['injectionwell_trajectory_table']
        friction_correlation = self.unit.parameters[
            'injectionwell_friction_correlation']
        length = []
        diameter = []
        angle = []
        roughness = []
        for ii in range(1, len(well_traj)):
            MD = well_traj[ii]['MD'] - well_traj[ii - 1]['MD']
            TVD = well_traj[ii]['TVD'] - well_traj[ii - 1]['TVD']

            length.append(MD)
            diameter.append(well_traj[ii]['ID'])
            angle.append((np.round(90 - np.arccos(TVD / MD) * 180 / np.pi, 2)) * np.pi / 180)
            roughness.append(well_traj[ii]['roughness'])

        well_param['diameter'] = np.array(diameter)  # well diameter in [m]
        well_param['length'] = np.array(length)  # well length in [m]
        well_param['angle'] = np.array(angle)  # well angle in [degree]
        well_param['roughness'] = roughness  # roughness of cells (mm)
        well_param['friction_correlation'] = friction_correlation

        self.model.update_parameters(well_param)

        pvt_param = dict()
        reservoir_unit = self.unit.to_units[0]
        pvt_param['RHOL'] = reservoir_unit.parameters['liquid_density']
        pvt_param['VISL'] = reservoir_unit.parameters['liquid_viscosity']
        self.model.PVT = PVTConstantSTP()
        self.model.PVT.update_parameters(pvt_param)

        time, injectionwell_flow = self.get_input_data('injectionwell_flow')
        time, injectionwell_wellhead_pressure = self.get_input_data(
            'injectionwell_wellhead_pressure')
        time, injectionwell_wellhead_temperature = self.get_input_data(
            'injectionwell_wellhead_temperature')

        u = dict()
        injectionwell_bottomhole_pressure = []
        for ii in range(1, self.loop.n_step):
            try:
                u['flowrate'] = -1 * injectionwell_flow[ii] / 3600
                u['pressure'] = injectionwell_wellhead_pressure[ii] * 1e5
                u['temperature'] = injectionwell_wellhead_temperature[ii] + 273.15
                u['direction'] = 'down'
                u['temperature_ambient'] = float(
                    self.unit.parameters['injectionwell_soil_temperature']) + 273.15

                x = []
                self.model.calculate_output(u, x)

                y = self.model.get_output()

                injectionwell_bottomhole_pressure.append(y['pressure_output'] / 1e5)
            except Exception as e:
                self.logger.warn("ERROR:" + repr(e))
                injectionwell_bottomhole_pressure.append(None)

        if injectionwell_bottomhole_pressure:
            self.write_output_data('injectionwell_bottomhole_pressure', time,
                                   injectionwell_bottomhole_pressure)
