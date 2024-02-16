from os import listdir
from os.path import join

from pandas import read_csv, read_excel

from data_container import DataContainer
from definitions import scen_to_subscen, network_name, select_time, pack_val, DifferentiateBy, Param, Calculation


class Scen:
    def __init__(self, sc, subscens):
        self.sc = sc
        self.ssc = subscens


class ReadPack:
    def __init__(self, network, scenario, param, calc, season=None, weeks=None, mean_by=DifferentiateBy.NONE):
        self.nw = pack_val(network)
        self.sc = pack_val(scenario)
        self.calc = pack_val(calc)
        self.param = pack_val(param)
        self.mean_by = mean_by
        assert (season is None and weeks is not None) or (
                season is not None and weeks is None), "Either season or week must be None"
        if season is not None:
            self.season = pack_val(season)
        elif weeks is not None:
            self.weeks = pack_val(weeks)


class SpatialPack(ReadPack):
    def __init__(self, network, scenario, param, calc, buses=None, season=None, weeks=None):
        super().__init__(network, scenario, param, calc, season, weeks)
        self.buses = pack_val(buses)


class TemporalPack(ReadPack):
    def __init__(self, network, scenario, param, calc, times_to_handle):
        super().__init__(network, scenario, param, calc, times_to_handle, None)
        self.times_to_handle = times_to_handle


class Reader:
    path = "input\\short"

    def read(self, pack):
        dc = DataContainer()
        for sc in pack.sc:
            inner_dir = join(self.path, sc.sc.value)
            for ssc in sc.ssc:
                scen_dir = join(inner_dir, scen_to_subscen[sc.sc](ssc).name)
                for nw in pack.nw:
                    for param in pack.param:
                        df_val, df_rel = self.read_abs(join(scen_dir, network_name[nw], "network_params"), param, pack)
                        for c in pack.calc:
                            if param == Param.PHASE and c == Calculation.MRE:
                                continue
                            if hasattr(pack, "season"):
                                for season in pack.season:
                                    df_val_s, df_sim_s = select_time(df_val, season=season), select_time(df_rel, season=season)
                                    dc.insert(df_val_s, df_sim_s, c, sc.sc, ssc, nw, param, pack.mean_by, season=season)
                            elif hasattr(pack, "week"):
                                for season in pack.week:
                                    df_val_s, df_sim_s = select_time(df_val, week=season), select_time(df_rel, week= season)
                                    dc.insert(df_val_s, df_sim_s, c, sc.sc, ssc, nw, param, pack.mean_by, week=season)
                            else:
                                dc.insert(df_val, df_rel, c, sc.sc, ssc, nw, param, pack.mean_by)
        return dc

    @staticmethod
    def read_abs(filename, param, pack):
        df_val = read_csv(f"{filename}_validation_{param.value}.csv", header=0, index_col=0)
        df_sim = read_csv(f"{filename}_simulation_{param.value}.csv", header=0, index_col=0)
        return select_time(df_val, pack), select_time(df_sim, pack)


def turn_to_csv():
    for inner_dir in listdir("input"):
        for dir in listdir(join("input", inner_dir)):
            for dd in listdir(join("input", inner_dir, dir)):
                for ddd in listdir(join("input", inner_dir, dir, dd)):
                    for f in listdir(join("input", inner_dir, dir, dd, ddd)):
                        if "xlsx" not in f:
                            continue
                        if "estimation" in f:
                            continue
                        content = read_excel(join("input", inner_dir, dir, dd, ddd, f), sheet_name=None,
                                             engine="openpyxl",
                                             header=0, index_col=0, skipfooter=5 if "difference" in f else 0)
                        for c, sheet in content.items():
                            sheet.to_csv(join("input", inner_dir, dir, dd, ddd, f"{f.replace('.xlsx', '')}_{c}.csv"))
