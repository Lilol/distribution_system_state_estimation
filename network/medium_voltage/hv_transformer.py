import utility.configuration as configuration


# Input of HV/MV transformer
class HighVoltageTransformer:
    def __init__(self):
        self.name = 'HV/MV'
        self.data = {'sn_mva': 40, 'vn_hv_kv': 120,
                     'vn_lv_kv': 20, 'vk_percent': 16,
                     'vkr_percent': 0, 'pfe_kw': 120,
                     'i0_percent': 0.019, 'shift_degree': 330}
        self.connecting_type = configuration.config.get("network.medium_voltage", 'connecting_type')
        self.connecting_fid = configuration.config.get("network.medium_voltage", 'connecting_fid')
        self.yellow_lines = []
