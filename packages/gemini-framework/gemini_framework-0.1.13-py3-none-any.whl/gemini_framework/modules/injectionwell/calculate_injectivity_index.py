from gemini_framework.abstract.unit_module_abstract import UnitModuleAbstract
from gemini_model.reservoir.injectivity_index import injectivity_index


class CalculateInjectivityIndex(UnitModuleAbstract):

    def __init__(self, unit):
        super().__init__(unit)

        self.model = injectivity_index()

        self.link_input('measured', 'injectionwell_flow')
        self.link_input('calculated', 'injectionwell_bottomhole_pressure')
        self.link_output('calculated', 'injectionwell_injectivity_index')

    def step(self, loop):
        self.loop = loop
        self.loop.start_time = self.get_output_last_data_time('injectionwell_injectivity_index')
        self.loop.compute_n_simulation()

        res_param = dict()
        res_param['reservoir_pressure'] = self.unit.to_units[0].parameters['reservoir_pressure']

        self.model.update_parameters(res_param)

        time, injectionwell_flow = self.get_input_data('injectionwell_flow')
        time, injectionwell_bottomhole_pressure = self.get_input_data(
            'injectionwell_bottomhole_pressure')

        u = dict()
        injectivity_index = []
        for ii in range(1, self.loop.n_step):
            try:
                u['flow'] = injectionwell_flow[ii]
                u['bottomhole_pressure'] = injectionwell_bottomhole_pressure[ii]

                x = []
                self.model.calculate_output(u, x)

                y = self.model.get_output()

                injectivity_index.append(y['injectivity_index'])
            except Exception as e:
                self.logger.warn("ERROR:" + repr(e))
                injectivity_index.append(None)

        if injectivity_index:
            self.write_output_data('injectionwell_injectivity_index', time, injectivity_index)
