from os.path import join

from pandas import read_excel, DataFrame, ExcelWriter

import utility.configuration as configuration


def collect_load_consumptions(na_values=0):
    input_frame = read_excel(join(configuration.config.get("paths", "pilot_path"),
                                  "Fogyasztok_" + str(
                                      configuration.config.get("input",
                                                               "network_id").value) + "_SAP_adatokkal_kieg.xlsx"),
                             engine='openpyxl', header=[0], index_col=0, na_values=na_values)
    input_frame = input_frame[["nappali_fogy", "vezerelt_fogy", "teljesitmeny"]]
    return input_frame.fillna(0).groupby(by=input_frame.index).sum()


def write_load_consumptions():
    load_consumptions = collect_load_consumptions()
    path = configuration.config.get("paths", "home_dir")
    writer = ExcelWriter(join(path, configuration.config.get("paths", "pilot_path"),
                              f"mef_{str(configuration.config.get('input', 'network_id').value)}.xlsx"), mode='w')
    load_consumptions.to_excel(writer, header=["nappali MEF (kWh)", "vezerelt MEF (kWh)"], index=True,
                               float_format="%.1f")
    writer.save()
