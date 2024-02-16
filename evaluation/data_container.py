from pandas import DataFrame, concat

from calculate import Calc
from definitions import Scenario1, Scenario2, Scenario3, DifferentiateBy

subscen_canonical_name = {
    Scenario1.NO_SM: "SC1b",
    Scenario1.SM: "SC1a",
    Scenario2.SC_2m: "SC2a",
    Scenario2.SC_2mm: "SC2b",
    Scenario3.CS: "SC3a",
    Scenario3.Profile: "SC3b",
    Scenario3.TMY: "SC3c",
}


class DataContainer:
    columns = ["Network", "Scenario", "Season", "Week", "Subscenario", "Parameter", "Error"]

    def __init__(self):
        self.df = DataFrame(
            columns=self.columns + ["Value"])

    def insert(self, df_val, df_sim, calc, scen, subscen, nw, param, mean_by, season=None, week=None):
        if mean_by == DifferentiateBy.NONE:
            new_row = {"Network": nw.value, "Scenario": scen.value, "Season": 0 if season is None else season.value,
                       "Week": 0 if week is None else week, "Subscenario": subscen_canonical_name[subscen],
                       "Parameter": param.value, "Error": calc.value,
                       "Value": Calc.calculate(df_val, df_sim, calc, mean_by)}
            idx = 0 if self.df.empty else self.df.index[-1] + 1
            self.df.loc[idx, :] = new_row
        else:
            df = DataFrame(columns=["Value"], data=Calc.calculate(df_val, df_sim, calc, mean_by).values)
            df[self.columns] = nw.value, scen.value, 0 if season is None else season.value, 0 if week is None else week,\
                subscen_canonical_name[subscen], param.value, calc.value
            self.df = df if self.df.empty else concat([self.df, df], axis="rows")

    def get(self, scen, subscen, nw, time=None):
        df = self.df[(self.df.Scenario == scen) & (self.df.Subscenario == subscen) & (self.df.Network == nw)]
        return df if time is None else df[time]
