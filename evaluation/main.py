from definitions import NetworkId, Scenario, Scenario1, Scenario3, Season, Param, Scenario2, Calculation, \
    DifferentiateBy
from reader import ReadPack, Reader, Scen, SpatialPack, TemporalPack
from visualization import plot

networks = [NetworkId.ID_20667, NetworkId.ID_44333, NetworkId.ID_18680, NetworkId.ID_44600]
scenarios = [Scenario.SC_1]
subscenarios1 = [Scenario1.SM, Scenario1.NO_SM]
subscenarios2 = [Scenario2.SC_2m, Scenario2.SC_2mm]
subscenarios3 = [Scenario3.CS, Scenario3.TMY, Scenario3.Profile]
seasons = [Season.Winter, Season.Spring, Season.Autumn, Season.Summer]
weeks = range(21)
all_calc = [Calculation.MAE, Calculation.RMS, Calculation.MRE]
to_read = {# "all": ReadPack(networks, Scen(Scenario.SC_1, subscenarios1), [Param.PHASE, Param.VOLTAGE], all_calc,
           #                    season=seasons, mean_by=DifferentiateBy.TIME),
           # "bynodes": ReadPack(networks, Scen(Scenario.SC_1, subscenarios1), [Param.PHASE, Param.VOLTAGE], all_calc,
           #                     season=seasons, mean_by=DifferentiateBy.NODE),
           # "all": ReadPack(networks, Scen(Scenario.SC_1, subscenarios1), [Param.PHASE, Param.VOLTAGE], all_calc,
           #                 season=seasons, mean_by=DifferentiateBy.NONE),
           # "scen2": ReadPack(networks, Scen(Scenario.SC_2, subscenarios2), [Param.PHASE, Param.VOLTAGE], all_calc,
           #                   season=seasons, mean_by=DifferentiateBy.TIME),
           # "scen3": ReadPack(networks, Scen(Scenario.SC_3, subscenarios3), [Param.PHASE, Param.VOLTAGE], all_calc,
           #                   season=seasons, mean_by=DifferentiateBy.TIME),
           "scen3_seasons": ReadPack(networks, Scen(Scenario.SC_3, subscenarios3),
                                        [Param.VOLTAGE], Calculation.RMS, season=seasons, mean_by=DifferentiateBy.TIME),
           }


def main():
    reader = Reader()
    for p, pack in to_read.items():
        dc = reader.read(pack)
        if p == "scen3_seasons":
            plot(f"{p}", dc, col_feature="Season", plot_type="bar")
        else:
            plot(f"{p}", dc, plot_type="bar")


if __name__ == '__main__':
    main()
