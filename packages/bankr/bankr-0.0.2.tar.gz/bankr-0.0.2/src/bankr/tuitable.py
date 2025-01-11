"""*Bankr* module for data presentation on TUI."""

import i18n
import sys

import pandas as pd
from prettytable import PrettyTable

from bankr.money import Money


def show_iban_stats(page: pd.DataFrame, iban: str) -> Money:
    """Statistics of an IBAN.

    It provides the number of Transactions, the first and last Transaction date,
    and the IBAN balance.
    """
    # TODO I18N
    try:
        first_transaction = page[page.iban == iban].date.min().strftime("%d.%m.%Y")
    except:  # noqa: E722
        first_transaction = "     keine"
    try:
        last_transaction = page[page.iban == iban].date.max().strftime("%d.%m.%Y")
    except:  # noqa: E722
        last_transaction = "     keine"
    try:
        value = Money.m(page[page.iban == iban].cents.sum() / 100.0)
    except:  # noqa: E722
        value = Money.m(0.0)

    # Print IBAN statistics   # TODO Improve f-strings, i18n
    print(f"    Anzahl der Buchungen:         {len(page[page.iban==iban]):>4}")
    print(f"    Erste Buchung:          {first_transaction}")
    print(f"    Letzte Buchung:         {last_transaction}")
    print(f"    Saldo:                 {value}\n")

    return value


def show_book_stats(book: pd.DataFrame, accounts: pd.DataFrame) -> None:
    """Book statistics.

    tbc
    """
    print(f"{book.shape[0]} {i18n.t('general.transactions')}\n")  # TODO Create a Pandas DataFrame beforehand

    iban: str = i18n.t("general.iban")
    tract: str = i18n.t("general.tract")
    balance: str = i18n.t("general.balance")
    first_tract: str = i18n.t("general.first_tract")
    last_tract: str = i18n.t("general.last_tract")
    account_desc: str = i18n.t("general.account_desc")

    stats: str = PrettyTable(field_names=[iban, tract, balance, first_tract, last_tract, account_desc])
    stats.align = "l"
    stats.align[tract] = "r"
    stats.align[balance] = "r"

    for account in accounts:
        iban = account["iban"]
        transactions = sum(book.iban == iban)
        balance = Money.m(book[book.iban == iban].cents.sum() / 100.0)
        try:
            first_transaction = book[book.iban == iban].date.min().strftime("%d.%m.%Y")
        except:  # noqa: E722
            first_transaction = "          "
        try:
            last_transaction = book[book.iban == iban].date.max().strftime("%d.%m.%Y")
        except:  # noqa: E722
            last_transaction = "          "
        desc = account["desc"][:40]
        stats.add_row([iban, transactions, balance, first_transaction, last_transaction, desc])
    print(stats, "\n")


def show_page(book: pd.DataFrame, year: int, month: int, cat: str, iban: str) -> str:
    """Show a table of Transactions or a Page of the Book.

    The arguments `year` and `month` limit the selected Transactions (`0` is unlimited).
    The selection can also be limited to a category or an IBAN (`""` is unlimited).
    The number of Transactions must not exceed 200.
    """
    book["year"] = book["date"].dt.year
    book["month"] = book["date"].dt.month
    page = book
    if year != 0:
        page = page[page["year"] == year]
        print(f"{i18n.t("general.year"):<15} {year}")
    if month != 0:
        page = page[page["month"] == month]
        print(f"{i18n.t("general.month"):<15} {month:02d}")
    if cat:
        page = page[page["cat"] == cat]
        print(f"{i18n.t("general.cat"):<15} {cat}")
    if iban:
        page = page[page["iban"] == iban]
        print(f"{i18n.t("general.iban"):<15} {iban}")
    tracts: int = page.shape[0]
    print(f"{i18n.t("general.transactions"):<15} {tracts}")
    if tracts > 200:
        return "overflow"  # To much Transactions selected

    # Headline of Transaction table
    pnum = "#"
    pdate = i18n.t("general.date")
    pamount = i18n.t("general.amount")
    pcat = i18n.t("general.cat")
    poffset = i18n.t("general.offset")
    pname = i18n.t("general.name")
    field_names = [pnum, pdate, pamount, pcat, poffset, pname]
    if iban:
        pprocess = i18n.t("general.process")
        field_names.extend([pprocess])
    else:
        piban = i18n.t("general.iban")
        field_names[2:2] = [piban]
    ppage: str = PrettyTable(field_names=field_names)
    ppage.align = "l"
    ppage.align[pnum] = "r"

    # Transactions table
    for n in range(0, tracts):
        pnum = n + 1
        pdate = page["date"].iloc[n].strftime("%d.%m.%Y")
        pamount = f"{Money.m(page["cents"].iloc[n]/100, page["curr"].iloc[n])}"
        pcat = f"{i18n.t('cats.' + page["cat"].iloc[n])}"
        poffset = page["offset"].iloc[n]
        pname = str(page["name"].iloc[n])[:20]
        field_names = [pnum, pdate, pamount, pcat, poffset, pname]
        if iban:
            pprocess = str(page["process"].iloc[n])[:20]
            field_names.extend([pprocess])
        else:
            piban = page["iban"].iloc[n]
            field_names[2:2] = [piban]
        ppage.add_row(field_names)
    print(ppage)

    # Transaction details
    while True:
        try:
            selection = input(f"{i18n.t("general.tractdetails")} ")
            if selection == "q":
                return "quit"  # Quit
            selint = int(selection)
            if selint < 1 or selint > tracts:
                raise ValueError
            break
        except ValueError:
            continue

    return page.index[selint - 1]


def show_income_per_interval(amounts: pd.DataFrame) -> None:
    """Create a Pretty Table of an "amounts table".

    See the documentation for an explanation of an "amounts table".
    """
    # Header
    cols = list(amounts)
    cols.remove("internal")
    amounts = amounts.drop(labels="internal", axis=1)
    pnames = ["Int."]  # TODO i18n
    for col in cols:
        pnames.append(i18n.t("cats." + col)[:3])
    ptable: str = PrettyTable(field_names=pnames)
    ptable.align = "r"

    # Rows
    index = list(amounts.index)  # TODO Translate total
    for row in range(amounts.shape[0]):
        ptable.add_row([index[row]] + [round(value) for value in amounts.iloc[row, :].to_list()])
    print(ptable)  # TODO Add legend


def show_transaction(book: pd.DataFrame, uuid: str, details: bool) -> None:
    """Show a Transaction, given by its UUID, in tabular form.

    The data source is the Book, a Page or a comparable data frame.
    """
    try:
        # Hint: This works only, if
        # (1) the uuid is the index of the book, and
        # (2) the uuid is of dtype string or category, not object.
        tract = book.loc[uuid]
    except KeyError:
        sys.exit(f"Bankr Error - Transaction {uuid} not found.")
    print("-" * 120)
    print(f"{i18n.t("general.uuid"):<20}{uuid}")
    print("-" * 120)
    print(f"{i18n.t("general.date"):<20}{tract["date"].strftime("%d.%m.%Y")}")
    print(f"{i18n.t("general.iban"):<20}{tract["iban"]}")
    print(f"{i18n.t("general.amount"):<20}{Money.m(tract["cents"]/100, tract["curr"])}")
    print(f"{i18n.t("general.cat"):<20}{i18n.t('cats.' + tract["cat"])}")
    if pd.notna(tract["valuta"]):
        print(f"{i18n.t("general.valuta"):<20}{tract["valuta"].strftime("%d.%m.%Y")}")
    if details:
        print(f"{i18n.t("general.offset"):<20}{tract["offset"]}")
    print(f"{i18n.t("general.name"):<20}{tract["name"]}")
    print(f"{i18n.t("general.process"):<20}{tract["process"]}")
    print(f"{i18n.t("general.desc"):<20}{tract["desc"][:100]}")
    if details:
        print(f"{i18n.t("general.creditor"):<20}{tract["creditor"]}")
        print(f"{i18n.t("general.mandate"):<20}{tract["mandate"]}")
        print(f"{i18n.t("general.customer"):<20}{tract["customer"]}")
        print(f"{i18n.t("general.source"):<20}{tract["source"]}")
    print("-" * 120)
