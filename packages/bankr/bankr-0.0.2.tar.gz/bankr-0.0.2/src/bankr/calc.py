"""*Bankr* module for data manipulation and statistics."""

import i18n
import sys
import time

import pandas as pd
from schwifty import IBAN

import bankr.tuitable as tt


# Helper - Transfer cents to euros
def _cents2euro(x: int) -> float:
    return x / 100.0


# Helper - Month to Term
def _month2term(month: int) -> int:
    if month < 7:
        term = 1
    else:
        term = 2
    return term


# Bankr - Helpers


def tract_existing(book: pd.DataFrame, uuid: str) -> bool:
    """Is a Transaction ID (UUID) existing in the Book?"""
    return uuid in book.index.values


def iban_valid(iban: str) -> bool:
    """Is a given IBAN string a valid IBAN?"""
    return IBAN(iban, allow_invalid=True).is_valid


# Operations on the Book


def add_page_to_book(page: pd.DataFrame, book: pd.DataFrame) -> pd.DataFrame:
    """Add a Page to the Book.

    This is an in memory and in place operation.
    """
    book = pd.concat([page, book], axis=0, ignore_index=False)
    book.sort_values(by=["date", "iban"], ascending=[False, True], inplace=True)
    return book


def autocat_tracts(page: pd.DataFrame, filtrs: list) -> None:
    """Auto-categorize a Page or the Book in place.

    Applies only to Transactions with cat == "none", since other, potential manually overruled
    categories must NOT be changed.
    *Technical remarks*
    (1) return not needed due to inplace operations.
    (2) Tilde operator ~ is an elementwise Not (needed, see "where" operator).
    (3) catcon["nones"] limits replacement to page["cat"] = "none". Index reset needed for "catcon" setup.
    (4) catcon["keys"] limits replacement, where the filter is fullfilled.
    """
    catcon = pd.DataFrame(columns=["nones", "keys"], index=range(page.shape[0]))
    page.reset_index(inplace=True)
    catcon.nones = page["cat"].str.contains("none")
    for filtr in filtrs:
        category = filtr["cat"]
        column = filtr["col"]
        keys = filtr["keys"]
        catcon["keys"] = page[column].str.contains(keys, case=False)
        page["cat"].where(~catcon.all(axis=1), other=category, inplace=True)
    page.set_index("uuid", inplace=True)


def mancat_tracts(book: pd.DataFrame, cats: list) -> None:
    """Manually categorize the Book in place.

    Loop over all Transactions with `cat == "none"`, and offer a manual change of the category.
    The manual categorization can be stopped at any time. In this case, the function will return a `"quit"` to the
    caller.
    """
    all_tracts = book.shape[0]
    none_tracts = sum(book["cat"] == "none")
    none = 1

    for n in range(all_tracts):
        tract = book.iloc[n]
        if tract["cat"] != "none":
            continue
        print("+" * 120)
        print(f"{i18n.t("general.transaction")} {none}/{none_tracts}")
        tt.show_transaction(book, tract.name, True)
        selection = select_category(cats)
        if selection == "quit":
            return
        book.loc[tract.name, "cat"] = selection
        print(f"{i18n.t("general.new_cat")}: {i18n.t("cats." + selection)}")
        none += 1
        time.sleep(0.5)


# Operations on Transations


def delete_transaction(book: pd.DataFrame, uuid: str) -> pd.DataFrame:
    """Delete a Transaction from the Book or from a Page."""
    try:
        return book.drop(index=uuid, inplace=False)
    except KeyError:
        sys.exit(f"Bankr Error - Transaction {uuid} not found.")


def select_transaction(book: pd.DataFrame, uuid: str) -> pd.Series:
    """Select a Transaction from the Book or a Page."""
    try:
        return book.loc[uuid]
    except KeyError:
        sys.exit(f"Bankr Error - Transaction {uuid} not found.")


def update_transaction(book: pd.DataFrame, tract: pd.Series) -> pd.DataFrame:
    """Update a Transaction of the Book or of a Page.

    If the Transaction ID is not existing, the Transaction will be appended.
    """
    uuid = tract.name
    try:
        book.loc[uuid] = tract
        return book
    except KeyError:
        sys.exit(f"Bankr Error - Transaction {uuid} could not be replaced or appended.")


def select_category(cats: list) -> str:
    """Provide a list of categories for selection.

    The categories are enumerated as they show up in `cats.yaml`.
    It returns the internal name of the category selected.
    """
    n = 0
    for cat in cats:
        print(f"[{n:>2}] - {i18n.t('cats.' + cat['cat']):<15}{cat['desc'][:58]}")
        n = n + 1
    print("-" * 80)
    while True:
        try:
            selection = input("Bankr Action - Select a category by [number] or (q)uit. ")
            if selection == "q":
                return "quit"  # Quit
            selection = int(selection)
            if selection < 0 or selection >= len(cats):
                raise ValueError
            break
        except ValueError:
            continue
    print("-" * 80)
    return cats[selection]["cat"]


# Statistics: Incomes


def calc_cat_per_interval(
    book: pd.DataFrame, year: int, span: int, *, quarter: bool, term: bool, full: bool
) -> pd.DataFrame:
    """Calculate the sum within a category per time interval.

    These sums are given as Pivot table with the time intervals as rows, and the categories in columns.
    The values are given as floats in the main currency.
    The time intervals can be months `timestr = "%Y-%m"` or years `timestr = "%Y"`.
    """
    # Limit to year, exit if no values
    book["year"] = book["date"].dt.year
    page = book
    if year != 0:
        page = book[(book["year"] >= year) & (book["year"] < (year + span))]
    if not page.shape[0]:
        sys.exit(f"Bankr Error - No values in {year}!")
    time = page["date"].dt.strftime("%Y-%m").rename("time")
    if quarter:
        time = page["year"].astype(str).rename("time")
        quarter = page["date"].dt.quarter.astype(str)
        time = time.str.cat(others=quarter, sep="-Q")
    if term:
        time = page["year"].astype(str).rename("time")
        term = page["date"].dt.month.apply(_month2term).astype(str)
        time = time.str.cat(others=term, sep="-T")
    if full:
        time = page["year"].astype(str).rename("time")
    page = pd.concat([page, time], axis=1, copy=False)

    # Calculate Pivot table
    stacked = page.groupby(["time", "cat"], as_index=False, observed=False)["cents"].sum()
    stacked["main"] = stacked["cents"].apply(_cents2euro)
    return stacked.pivot(index="time", columns="cat", values="main")


def append_totals(amounts: pd.DataFrame) -> pd.DataFrame:
    """Calculate incomes/expenses/balances per row, and column totals.

    It expects an "amounts-type" dataframe. Firstly, it appends it with three columns,
    the total incomes per time interval (row), the total expenses, and the balance (sum).
    Secondly, it adds a row with column totals.
    """
    amounts.loc["total"] = amounts.sum(axis=0)
    income = amounts.mask(amounts < 0, 0)
    income["internal"] = 0
    expense = amounts.mask(amounts > 0, 0)
    expense["internal"] = 0
    amounts["income"] = income.sum(axis=1)
    amounts["expense"] = expense.sum(axis=1)
    amounts["balance"] = amounts["income"] + amounts["expense"]

    return amounts  # TODO Remove categories, return totals only
