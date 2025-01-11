"""*Bankr* module for plot presentation on TUI."""

import i18n

import pandas as pd
import plotext as plt


def plot_cat_per_interval(amounts: pd.DataFrame, plot_title: str) -> None:
    """Stacked bar plot of the time intervals."""
    cats = list(amounts.columns)
    time = list(amounts.index)
    labels = []
    values = []
    for n in range(amounts.shape[1]):
        values.append(list(amounts[cats[n]]))
        labels.append(i18n.t("cats." + cats[n]))
    plt.stacked_bar(time, values, label=labels)
    plt.theme("pro")
    plt.hline(0, color="white")
    plt.title(plot_title)
    plt.plot_size(width=None, height=plt.th() / 2)
    plt.xlabel(i18n.t("general.date"))
    plt.ylabel(i18n.t("general.amount"))
    plt.show()
