from pathlib import Path

import panel as pn
import pandas as pd
import hvplot.pandas  # noqa

import bankr.calc as bc
import bankr.files as bf

# Debugger
# import bankr.utils as utils

# utils.debugger()

# Bankr Data Import

bankr_path = Path("./bankr.yaml").resolve()
params = bf.read_bankr_yaml(bankr_path)
data_path = Path(params["DATA_PATH"]).resolve()
accounts = bf.read_bankr_yaml(data_path / "accounts.yaml")
book = bf.unpickle_book(data_path)

# Panel init

pn.extension(design="material")


# Functions for Panel Binds


def refresh_panel(book: pd.DataFrame, first_year: str, years: str):
    quarter: bool = False
    term: bool = False
    full: bool = False
    if int(years) == 2 or int(years) == 3:
        quarter = True
    if int(years) == 4:
        term = True
    if int(years) == 5:
        full = True
    amounts = bc.calc_cat_per_interval(book, int(first_year), int(years), quarter=quarter, term=term, full=full)
    amounts = amounts.drop(labels="internal", axis=1)

    return amounts.hvplot.bar(stacked=True, width=1200, height=750)


def refresh_table(book: pd.DataFrame, first_year: str, years: str):
    quarter: bool = False
    term: bool = False
    full: bool = False
    if int(years) == 2 or int(years) == 3:
        quarter = True
    if int(years) == 4:
        term = True
    if int(years) == 5:
        full = True
    amounts = bc.calc_cat_per_interval(book, int(first_year), int(years), quarter=quarter, term=term, full=full)
    amounts = amounts.drop(labels="internal", axis=1)

    return bc.append_totals(amounts)


# Sidebar definition

sidebar = pn.pane.Markdown("""
    # Dashboards
    ## Test Lorem Ipsum
    [Secondary](/app-sec)
    """)

# Input & Output Widgets

first_year = pn.widgets.Select(name="First Year", options=["2021", "2022", "2023", "2024"])
years = pn.widgets.Select(name="Years", options=["1", "2", "3", "4", "5"])
row = pn.Row("## Select Interval", first_year, years, styles=dict(background="Whitesmoke"))

plot = pn.bind(refresh_panel, book=book, first_year=first_year, years=years)
totals = pn.bind(refresh_table, book=book, first_year=first_year, years=years)
tabs = pn.Tabs(("Plot", plot), ("Table", totals), dynamic=True)

# Panel Definition

pn.template.FastListTemplate(
    site="Bankr",
    title="Main Dashboard",
    sidebar=sidebar,
    main=[row, tabs],
).servable()
