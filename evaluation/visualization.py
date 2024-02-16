from math import sqrt
from os.path import join

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from definitions import get_param_name, Calculation, Param

matplotlib.use("Qt5Agg")

output = "D:\\OneDrive_BME\\Publikációk\\PowerSystems\\actaPolytechnica\\figures"
plotkind = {"barplot": sns.barplot, "histplot": sns.histplot, "scatterplot": sns.scatterplot, "boxplot": sns.boxplot}

font_size = 26
font_scale = 2
matplotlib.rc('font', size=font_size)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
matplotlib.rc('text', usetex=True)
matplotlib.rc('legend', fontsize=16)

fig_width_pt = 800
inches_per_pt = 1.0 / 72.27
golden_mean = (sqrt(5) - 1.0) / 1.5
fig_width = fig_width_pt * inches_per_pt
fig_height = fig_width * golden_mean * 0.8
fig_size = [fig_width, fig_height]
plt.rcParams['figure.figsize'] = fig_size

feature_names = {"node_voltage_angle_deg": "Node voltage phase [rad]",
                 "node_voltage_pu": "Node voltage amplitude [p.u.]"}


def plot(title, data_container, plot_type, row_feature="Parameter", col_feature="Error",
         group_by="Network", split_by="Subscenario"):
    df = data_container.df.sort_values([group_by, "Subscenario", "Parameter"])
    g = sns.catplot(col=col_feature, row=row_feature, x=group_by, hue=split_by, y="Value", kind=plot_type, dodge=True,
                    data=df, sharey=True, col_order=["Winter", "Spring", "Summer", "Autumn"])
    for (row_key, col_key), ax in g.axes_dict.items():
        if len(ax.lines) == 0:
            ax.axis('off')
            ax.set_title("")
            continue
        try:
            ax.set_ylabel(f"{get_param_name(Param(row_key), Calculation(col_key))}")
        except:
            ax.set_ylabel(f"{get_param_name(Param.VOLTAGE, Calculation.RMS)}")
        try:
            ax.set_title(f"{Calculation(col_key).value}")
        except:
            ax.set_title(f"{col_key}")
        ax.set_xlabel(group_by)
    plt.subplots_adjust(wspace=0.8)
    # g.legend.set(bbox_to_anchor=(0.9, 0.75), title="Scenario")
    g.legend.set(bbox_to_anchor=(0.98, 0.75), title="Scenario")
    plt.tight_layout()
    # plt.subplots_adjust(wspace=0.8)
    # plt.show()
    g.savefig(join(output, f"fig_{title}.png"))
    plt.close()

    # subplot_titles = df[split_by].unique()
    # nx = len(subplot_titles) // rows + len(subplot_titles) % rows
    # ny = rows
    # fig, axes = plt.subplots(ny, nx, sharex=True, sharey=True, figsize=(nx*5, ny*5))
    # for ax, feature in zip(axes.ravel(), subplot_titles):
    #     dff = df[df[split_by] == feature]
    # if filter_for is not None:
    #     for feature, value in filter_for.items():
    #         df = df[df[feature] == value]
    #         ax.set_title(feature)
