from calendar import monthrange
from datetime import datetime
from enum import Enum
from glob import glob
from os.path import join

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import sqrt
from pandas import to_datetime, date_range, DateOffset, DataFrame, read_csv, concat, Timedelta, read_excel

matplotlib.use("Qt5Agg")


class Network(Enum):
    BARACS = 18680
    GYOR = 20667
    BALATONAKALI = 44333
    BALATONSZEPEZD = 44600


output = "D:\\OneDrive_BME\\Publikációk\\PowerSystems\\actaPolytechnica\\figures"


def read_slp():
    prof_file = "D:\\OneDrive_BME\\OtherResearch\\utils\\Profilok_2021.xlsx"
    profiles = read_excel(prof_file, header=0, index_col=0)
    profiles.loc[:, "Datetime"] = profiles.index.astype("str") + " " + profiles["Negyedórák"].astype("str")
    profiles.loc[profiles['Datetime'].str.contains('24:00'), "Datetime"] = to_datetime(
        profiles.loc[profiles['Datetime'].str.contains('24:00'), 'Datetime'].str.replace('24:00', '00:00')) + Timedelta(
        days=1)
    profiles.index = to_datetime(profiles["Datetime"])
    return profiles


fontsize = 32
font_scale = 2
matplotlib.rc('font', size=fontsize)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
matplotlib.rc('legend', fontsize=16)

fig_width_pt = 500
inches_per_pt = 1.0 / 72.27
golden_mean = (sqrt(5) - 1.0) / 2.0
fig_width = fig_width_pt * inches_per_pt
fig_height = fig_width * golden_mean
fig_size = [fig_width, fig_height]
plt.rcParams['figure.figsize'] = fig_size

profiles = read_slp()


def plot_control_signal():
    control_signal = [1] * 5 + [0] * 7 + [1] * 2 + [0] * 6 + [1] * 4
    day = datetime(2019, 7, 19)
    dates = date_range(day, day + DateOffset(hours=23), freq='H')
    control_signal = DataFrame(control_signal, index=dates, columns=["Control signal"])

    fig, ax = plt.subplots()
    ax.plot(control_signal, "o-", color="darkgrey")
    # ax.plot(cont, "o-", color="blue")
    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["OFF", "ON"])
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, bottom=0.229, left=0.074, right=0.959, hspace=0.2, wspace=0.2)
    # plt.show()
    fig.savefig("output\\figures\\control_signal.pdf")
    plt.close()


def plot_profiles(day=datetime(2019, 7, 19), nw=Network.BARACS):
    individual_profiles = read_csv(join(output, f"{nw.value}", "profiles.csv"), header=0, index_col=0)
    individual_profiles.loc[:, "Hot water profile"] = individual_profiles.sum(axis="columns")
    individual_profiles.index = to_datetime(individual_profiles.index)

    dates = date_range(day, day + DateOffset(hours=23), freq='H')
    cont = profiles.loc[dates, ["Vezérelt", "Lakosság vidék", "PV"]]
    ind = individual_profiles.loc[dates, ["Hot water profile"]]
    cont = concat([cont, ind], axis="columns")
    cont /= cont.max()
    fig, ax = plt.subplots()
    colors = ("#7A0017", "black", "green", "blue")
    markers = ("--", "-", ":", "-.")
    labels = ("$\mathrm{Controlled}$", "$\mathrm{Residential}$", "$\mathrm{PV}$", "$\mathrm{Hot\ water}$")
    for c, color, m, l in zip(cont.columns, colors, markers, labels):
        ax.plot(cont[c], m, color=color, label=l, linewidth=3)

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=fontsize)
    ax.legend(loc="upper left", fontsize=fontsize + 2)
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.164, left=0.058, right=0.959, hspace=0.2, wspace=0.2)
    # plt.show()
    fig.savefig("output\\figures\\profiles.pdf")
    plt.close()


def plot_controlled(profiles, day=datetime(2019, 1, 12), year=2021, select_col_no=11):
    dfc = profiles[["Vezérelt"]]
    dfc = dfc.rename(columns={"Vezérelt": "Profile"})
    cont_input = "D:\\OneDrive_BME\\RecOpt\\oipe2023_presentation\\input\\controlled.csv"
    dfc2 = read_csv(cont_input, delimiter=',', header=None)
    dfc2.index = to_datetime(date_range(start=datetime(year, 1, 1), end=datetime(year + 1, 1, 1), freq="15T"))[:-1]

    dr = pd.date_range(day, day + DateOffset(hours=23), freq='15T')
    ut_ptofile = dfc.join(dfc2)
    ut_ptofile = ut_ptofile.loc[dr, :]
    ut_ptofile.Profile *= ut_ptofile[select_col_no].sum()

    fig, ax = plt.subplots(figsize=(13, 8))
    cols = ["Profile", select_col_no]
    colors = ("green", "blue")
    markers = ("--", "-")
    labels = ("Profile", "Historical data")

    for c, color, m, l in zip(cols, colors, markers, labels):
        ax.plot(ut_ptofile[c], m, color=color, label=l, linewidth=4)

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_ylabel("Consumed energy (kWh)", fontsize=fontsize)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=fontsize)
    ax.legend(loc="upper left", fontsize=fontsize + 2)
    plt.tight_layout()
    # plt.subplots_adjust(top=0.955, bottom=0.139, left=0.067, right=0.964, hspace=0.2, wspace=0.2)
    # plt.show()
    fig.savefig(join(output, f"controlled_{day:%Y-%m-%d}.png"))
    plt.close()


def process_tmy():
    path = "D:\\OneDrive_BME\\Lendulet_T1.2-T3.2\\Measurements\\RE_HMKE_scenarios\\input\\Balatonakali"
    tmy_file = join(path, "tmy_46.883_17.752_2005_2020.csv")
    tmy_data = read_csv(tmy_file, skiprows=16, header=0, index_col=0, skipfooter=12)
    tmy_data.index = to_datetime(tmy_data.index, format="%Y%m%d:%H%M")
    tmy_data.index = tmy_data.index.map(lambda x: x.replace(year=year))
    tmy_data = tmy_data[['G(h)']]
    tmy_data = tmy_data.resample('15T').asfreq().interpolate(method="spline", order=3)
    tmy_data[tmy_data < 0] = 0
    tmy_data.index = tmy_data.index + DateOffset(hours=1)
    return tmy_data


def process_cs():
    path = "D:\\OneDrive_BME\\Lendulet_T1.2-T3.2\\Measurements\\RE_HMKE_scenarios\\input\\Balatonakali"
    cs_data = DataFrame()
    for file in glob(join(path, "Dailydata*.csv")):
        dd = read_csv(file, skiprows=7, header=0, index_col=0, skipfooter=7, delim_whitespace=True)
        month = file.replace(path+"\\", "").replace(".csv", "").replace("Dailydata_46.883_17.752_SA2_", "").replace("_0deg_0deg", "")
        dd["time"] = f"{year}-{month}-01-" + dd.index.astype("str")
        dd.index = to_datetime(dd["time"], format="%Y-%m-%d-%H:%M")
        dd.loc[datetime(year, int(month), 1, 23, 45), :] = 0
        dd= dd.drop(columns=["time"])
        ndays = monthrange(year, int(month))[1]
        dd = dd.resample('15T').asfreq().interpolate("spline", order=3)
        dd[dd < 0] = 0
        dd = DataFrame(np.tile(dd.values, [ndays, 1]), columns=dd.columns)
        date_index = date_range(start=f'{year}-{month}-01', end=f'{year if int(month) < 12 else year+1}-{int(month)+1 if int(month) < 12 else 1}-01', freq="15T")
        dd.index = date_index[:len(dd.index)]
        cs_data = concat([cs_data, dd], axis="rows")
    return cs_data


def plot_pv(profile, tmy_data, cs_data, day, year=2021):
    df = profile[["PV"]]
    df = df.rename(columns={"PV": "Profile"})
    df *= 1000 * 4

    df = df.join(tmy_data).join(cs_data)
    dr = pd.date_range(day, day + DateOffset(hours=23), freq='15T')
    df = df.loc[dr, :] / 1000
    fig, ax = plt.subplots(figsize=(13, 8))
    cols = ["Profile", "G(h)", "G(i)"]
    colors = ("green", "blue", "black")
    markers = ("--", "-", ":")
    labels = ("Profile", "TMY", "CS")

    for c, color, m, l in zip(cols, colors, markers, labels):
        ax.plot(df[c], m, color=color, label=l, linewidth=4)

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_ylabel("Energy produced (kWh)", fontsize=fontsize)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=fontsize)
    ax.legend(loc="upper left", fontsize=fontsize + 2)
    plt.tight_layout()
    # plt.show()
    fig.savefig(join(output, f"pv_{day:%Y-%m-%d}.png"))
    plt.close()


def plot_residential(profiles, day, year=2021,
                     sm="LP_1_HU000120-11-S00000000000000023919_202001010000_20201231000000_20210930160040",
                     select_col_no=10):
    dfr = profiles[["Lakosság vidék"]]
    dfr = dfr.rename(columns={"Lakosság vidék": "Profile"})

    metered_data = f"D:\\OneDrive_BME\\Lendulet_T1.2-T3.2\\Measurements\\Összesített smart mérő adatok\\MKP-adatok\\{sm}.xlsx"
    md = read_excel(metered_data, skiprows=6, header=0, index_col=0)
    md.index = to_datetime(md.index) + DateOffset(years=year - md.index[0].year, minutes=-15)
    md = md[["Érték"]]

    dfr2 = read_csv("input\\residential2.csv", delimiter=',', header=0, index_col=0)
    dfr2.index = to_datetime(date_range(start=datetime(year, 1, 1), end=datetime(year + 1, 1, 1), freq="15T"))[
                 :len(dfr2.index)]
    dfr2 /= 4
    dfr2 = dfr2[[f"{select_col_no}"]]

    dr = pd.date_range(day, day + DateOffset(hours=23), freq='15T')
    df = dfr.join(dfr2).join(md)
    df = df.loc[dr]
    df.Profile *= df["Érték"].sum()

    fig, ax = plt.subplots(figsize=(13, 8))
    cols = ["Profile", "Érték", f"{select_col_no}"]
    colors = ("green", "blue", "black")
    markers = ("--", "-", ":")
    labels = ("Profile", "Historical data", "Smart Metered data")

    for c, color, m, l in zip(cols, colors, markers, labels):
        ax.plot(df[c], m, color=color, label=l, linewidth=4)

    myFmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_ylabel("Consumed energy (kWh)", fontsize=fontsize)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=fontsize)
    ax.legend(loc="upper left", fontsize=fontsize + 2)
    plt.tight_layout()
    # plt.show()
    fig.savefig(join(output, f"residential_{day:%Y-%m-%d}.png"))
    plt.close()


# plot_very_small_profile("PV", "pv")

# plot_hot_water_and_controlled_together()

# plot_profiles()

def convert():
    df = DataFrame()
    import scipy.io
    mm = \
        scipy.io.loadmat("input\\Fogy_szcen.mat", squeeze_me=False, struct_as_record=False, simplify_cells=True)[
            "SC2mm_L"]
    DataFrame(mm).to_csv("input\\residential2.csv")
    for week in mm:
        weekly_cons = week["residential"]
        idf = DataFrame()
        for cl, frame in weekly_cons["sc_2mm"].items():
            idf = concat([idf, DataFrame(frame)], axis="columns")
        idfr = DataFrame()
        for cl, frame in weekly_cons["reference"].items():
            idfr = concat([idfr, DataFrame(frame)], axis="columns")
        df = concat([df, idf, idfr], axis="rows")
    df.to_csv("input\\residential.csv")


# convert()
year = 2021
profile = read_slp()
cs_data = process_cs()
tmy_data = process_tmy()
# plot = ["pv", "residential", "controlled"]
plot = ["residential"]
for day in (datetime(year, 1, 10), datetime(year, 7, 15), datetime(year, 10, 3)):
    for p in plot:
        if p == "pv":
            plot_pv(profile, tmy_data, cs_data, day=day, year=year)
        elif p == "residential":
            plot_residential(profile, day=day, year=year, select_col_no=0)
        elif p == "controlled":
            plot_controlled(profile, day=day, year=year)
