import numpy as np

from definitions import Calculation


def rms(df_val, df_sim, mean_by):
    df = (df_val - df_sim) ** 2
    return np.sqrt(df.mean(axis=mean_by.value))


def mae(df_val, df_sim, mean_by):
    return (df_val - df_sim).abs().mean(axis=mean_by.value)


def var(df_val, df_sim, mean_by):
    return (df_val - df_sim).var(axis=mean_by.value)


def mre(df_val, df_sim, mean_by):
    return ((df_val - df_sim) / df_val).mean(axis=mean_by.value)


calc_to_fun = {
    Calculation.RMS: rms,
    Calculation.MAE: mae,
    Calculation.MRE: mre,
    Calculation.VAR: var
}


class Calc:
    def __init__(self):
        pass

    @staticmethod
    def calculate(df_val, df_sim, kind, mean_by):
        return calc_to_fun[kind](df_val, df_sim, mean_by)
