"""The commands of *Bankr*'s command line interface."""

import click
import os
import i18n

from pathlib import Path
from pyfiglet import Figlet

import bankr.calc as bc
import bankr.files as bf

import bankr.tuiplot as tp
import bankr.tuitable as tt

bankr_path = Path("./bankr.yaml").resolve()
params = bf.read_bankr_yaml(bankr_path)
data_path = Path(params["DATA_PATH"]).resolve()


# Helper - Print title
def _bankr_title(subtitle: str) -> None:
    # Clear CLI
    if os.name == "nt":  # On Windblows
        _ = os.system("cls")
    else:  # On valuable and expensive Linux
        _ = os.system("clear")
    print(Figlet().renderText("Bankr"))
    click.echo(f"### {i18n.t('general.title')} ###", nl=False)
    if subtitle:
        click.echo(f" - {subtitle}\n")
    else:
        click.echo("\n")


# Helper - Print info
def _bankr_info(info: str, verbose: bool) -> None:
    if verbose:
        click.echo(f"Bankr {i18n.t('general.info')} - {info}")


# Helper - Test command for development
@click.command()
def test():
    # book = bf.unpickle_book(data_path)
    click.echo("This is a command used for development only.")


@click.command()
@click.argument("csv_file")
@click.option("-a", "--add", is_flag=True, help="Add the auto-cat Page to the Book")
@click.option("-v", "--verbose", is_flag=True, help="Provide info about processing steps")
def parse(csv_file: str, add: bool, verbose: bool):
    """Parse CSV for a Page, and eventually add it to the Book.

    A summary of the Transactions of the Page, and the expectable changes of the Book are presented.
    The Book is not changed in Parse Mode. If in Add Mode, an auto categorized Page is added to the Book.
    """
    subtitle = "Parse Mode"
    if add:
        subtitle = "Add Mode"
    _bankr_title(subtitle)

    # Parse CSV to Page
    page = bf.parse_csv(data_path, csv_file)
    _bankr_info(f"{csv_file} {i18n.t('general.parsed')}", verbose)
    book = bf.unpickle_book(data_path)

    # Auto-categorize Page
    filtrs = bf.read_bankr_yaml(data_path / "filters.yaml")
    bc.autocat_tracts(page, filtrs)
    _bankr_info(f"{i18n.t('general.page')} {i18n.t('general.categorized')}", verbose)
    if add:
        # Import Page to Book, and save it
        book = bc.add_page_to_book(page, book)
        book = bf.condition_book(book, data_path, "%d.%m.%Y")
        _bankr_info(f"{i18n.t('general.page')} {i18n.t('general.imported')}", verbose)
        bf.pickle_book(book, data_path)
        _bankr_info(f"{i18n.t('general.book')} {i18n.t('general.saved')}", True)
    else:
        # Print statistics of the relevant IBAN
        iban = csv_file.split("-")[0]
        click.echo(f"- {i18n.t('general.page')}:")
        page_balance = tt.show_iban_stats(page, iban)
        click.echo(f"- {i18n.t('general.book')}:")
        book_balance = tt.show_iban_stats(book, iban)
        click.echo(  # TODO i18n
            f"  Neuer Saldo des {i18n.t('general.book')}s:   {book_balance + page_balance}\n"
        )
        while True:
            selection = input("Bankr Action - Show Transactions of the created Page (y/n)? ")  #
            if selection == "y":
                tract = tt.show_page(page, 0, 0, "", "")
                if tract == "overflow":
                    _bankr_info("Maximum number of Transactions is 200.", True)
                    break
                elif tract == "quit":
                    break
                else:
                    tt.show_transaction(page, tract, True)
                    break
            elif selection == "n":
                break


@click.command()
@click.argument("iban")
def add(iban: str):
    """Add a Transaction to the Book."""
    _bankr_title("Addition Mode")
    # TODO Check, if string iban is a valid IBAN in the Book, stop otherwise
    # TODO Commands add and edit have quite similar code snippets
    book = bf.unpickle_book(data_path)
    page = bf.create_transaction(iban)
    tract = str(page["uuid"][0])
    page.set_index("uuid", inplace=True)
    page = bf.condition_book(page, data_path, "%d.%m.%Y")
    book = bc.add_page_to_book(page, book)
    book = bf.condition_book(book, data_path, "%d.%m.%Y")
    tt.show_transaction(book, tract, True)
    while True:
        selection = input("Bankr Action - Add this Transaction to the Book (y/n)? ")
        if selection == "y":
            bf.pickle_book(book, data_path)
            _bankr_info(f"Transaction {tract} added.", True)
            break
        elif selection == "n":
            _bankr_info("No addition.", True)
            break


@click.command()
@click.argument("uuid")
def edit(uuid: str):
    """Edit a Transaction in the Book."""
    _bankr_title("Edit Transaction Mode")
    book = bf.unpickle_book(data_path)
    tract = bc.select_transaction(book, uuid)
    print("-" * 120)
    print(f"IBAN:        {tract["iban"]}")
    print(f"Transaction: {tract.name}")
    print("-" * 120)
    tract = bf.edit_transaction(tract)
    book = bc.update_transaction(book, tract)
    tt.show_transaction(book, uuid, True)
    while True:
        selection = input("Bankr Action - Update this Transaction within the Book (y/n)? ")
        if selection == "y":
            bf.pickle_book(book, data_path)
            _bankr_info(f"Transaction {uuid} updated.", True)
            break
        elif selection == "n":
            _bankr_info(f"No update of Transaction {uuid}.", True)
            break


@click.command()
@click.argument("uuid")
def delete(uuid: str):
    """Delete a Transaction from the Book.

    The Transaction to delete is defined by its Transaction ID or UUID.
    """
    _bankr_title("Deletion Mode")
    book = bf.unpickle_book(data_path)
    tt.show_transaction(book, uuid, True)
    while True:
        selection = input("Bankr Action - Delete this Transaction from the Book (y/n)? ")
        if selection == "y":
            book = bc.delete_transaction(book, uuid)
            bf.pickle_book(book, data_path)
            _bankr_info(f"Transaction {uuid} deleted.", True)
            break
        elif selection == "n":
            _bankr_info("No deletion.", True)
            break


@click.command()
@click.option("-y", "--year", type=click.IntRange(min=1900, max=2100, clamp=True), help="First year to plot")
@click.option("-s", "--span", type=click.IntRange(min=1, max=10, clamp=True), help="Number of years to plot")
@click.option("-q", "--quarter", is_flag=True, help="Plot quarters")
@click.option("-t", "--term", is_flag=True, help="Plot terms/half-years")
@click.option("-f", "--full", is_flag=True, help="Plot full years")
def stats(year: int, span: int, quarter: bool, term: bool, full: bool):
    """Statistics of the Book or per time interval.

    Statistics of the Book:
    The number of transactions per IBAN, its current account balance, and the date of the
    first/last transaction are shown.

    Transaction Statistics:
    Amounts per category and time interval.
    """
    accounts = bf.read_bankr_yaml(data_path / "accounts.yaml")
    book = bf.unpickle_book(data_path)
    if not span:
        span = 200
    if year:
        _bankr_title(i18n.t("general.statistics"))
        amounts = bc.calc_cat_per_interval(book, year, span, quarter=quarter, term=term, full=full)
        amounts = bc.append_totals(amounts)
        tt.show_income_per_interval(amounts)
    else:
        _bankr_title(f"{i18n.t('general.book_stats')}")
        tt.show_book_stats(book, accounts)


@click.command()
@click.option("-m", "--manual", is_flag=True, help="Manually categorize Transactions without category")
@click.option("-u", "--uuid", type=click.STRING, help="Manually categorize a Transaction with a given ID")
def cat(manual: bool, uuid: str):
    """Categorize Transactions of a Page or the Book.

    Basis of the automatic categorization is `filters.yaml`. Manual and auto cat work only
    on transactions without a category.
    """
    book = bf.unpickle_book(data_path)
    if uuid and bc.tract_existing(book, uuid):
        cats = bf.read_bankr_yaml(data_path / "cats.yaml")
        _bankr_title("TractID Mode")
        tt.show_transaction(book, uuid, True)
        selection = bc.select_category(cats)
        if selection != "quit":
            book.loc[uuid, "cat"] = selection
        _bankr_info(
            f"{i18n.t('general.uuid')} {uuid} {i18n.t('general.categorized')}",
            True,
        )
    elif uuid and not bc.tract_existing(book, uuid):
        click.echo("Bankr Error - Invalid Transaction ID")
        return
    elif manual:
        cats = bf.read_bankr_yaml(data_path / "cats.yaml")
        _bankr_title("Manual Mode")
        bc.mancat_tracts(book, cats)
        _bankr_info(
            f"{i18n.t("general.book")} {i18n.t('general.categorized')} - {sum(book["cat"] == "none")} {i18n.t("general.wo_cat")}",
            True,
        )
    else:
        filtrs = bf.read_bankr_yaml(data_path / "filters.yaml")
        _bankr_title("Auto Mode")
        bc.autocat_tracts(book, filtrs)  # noqa: F823
        _bankr_info(
            f"{i18n.t("general.book")} {i18n.t('general.categorized')} - {sum(book["cat"] == "none")} {i18n.t("general.wo_cat")}",
            True,
        )
    bf.pickle_book(book, data_path)
    _bankr_info(f"{i18n.t('general.book')} {i18n.t('general.saved')}", True)


@click.command()
@click.option("-y", "--year", type=click.IntRange(min=1900, max=2100, clamp=True), help="Year to show")
@click.option("-m", "--month", type=click.IntRange(min=1, max=12, clamp=True), help="month to show")
@click.option("-c", "--cat", type=click.STRING, help="Category to show")  # TODO Apply i18n
@click.option("-i", "--iban", type=click.STRING, help="IBAN to show")
def show(year: int, month: int, cat: str, iban: str):
    """Show the Transactions of an interval or an IBAN.

    Options restrict the displayed Transactions to the given time interval (month or year),
    or limit these to an IBAN.
    """
    if not year:
        year = 0
    if not month:
        month = 0
    if not iban:
        iban = ""
    elif not bc.iban_valid(iban):
        iban = ""
    book = bf.unpickle_book(data_path)
    _bankr_title("Page Mode")
    tract = tt.show_page(book, year, month, cat, iban)
    if tract == "overflow":
        _bankr_info("Maximum number of Transactions is 200.", True)
    elif tract == "quit":
        return
    else:
        tt.show_transaction(book, tract, True)


@click.command()
@click.option("-y", "--year", type=click.IntRange(min=1900, max=2100, clamp=True), help="First year to plot")
@click.option("-s", "--span", type=click.IntRange(min=1, max=10, clamp=True), help="Number of years to plot")
@click.option("-q", "--quarter", is_flag=True, help="Plot quarters")
@click.option("-t", "--term", is_flag=True, help="Plot terms/half-years")
@click.option("-f", "--full", is_flag=True, help="Plot full years")
def plot(year: int, span: int, quarter: bool, term: bool, full: bool):
    """Plot time information on CLI.

    Plot the amounts within a category per time interval on CLI. The time interval
    is a month, a quarter, a term or half-year, or a year. When ambiguous, larger
    intervals win.

    Limitations: Very small fractions of the total amount can not be plotted on CLI.
    Therefore, it can only provide a first impression of the actual distribution.
    """
    book = bf.unpickle_book(data_path)
    if not year:
        year = 0
    if not span and year:
        span = 1
    amounts = bc.calc_cat_per_interval(book, year, span, quarter=quarter, term=term, full=full)
    plot_title = i18n.t("general.monthly")
    if quarter:
        plot_title = i18n.t("general.quarterly")
    if term:
        plot_title = i18n.t("general.per_term")
    if full:
        plot_title = i18n.t("general.yearly")
    _bankr_title("")
    tp.plot_cat_per_interval(amounts, plot_title)


@click.command()
@click.argument("transfer", type=click.Choice(["import", "export"]))
def excel(transfer: str):
    """Import/export the Book from/into an Excel file (not valid in v0.0.1!).

    Limitation: The Excel version of the Book has no Excel data formating, and it uses the internal data
    representation (no i18n).
    """
    if transfer == "import":
        _bankr_title("Excel Import")
        book = bf.unexcel_book(data_path)
        book = bf.condition_book(book, data_path, "%d.%m.%Y")
        _bankr_info(
            f"{i18n.t('general.book')} {i18n.t('general.imported')} {i18n.t('general.from_excel')}",
            True,
        )
        bf.pickle_book(book, data_path)
        _bankr_info(f"{i18n.t('general.book')} {i18n.t('general.saved')}", True)
    else:
        _bankr_title("Excel Export")
        book = bf.unpickle_book(data_path)
        bf.excel_book(book, data_path)
        _bankr_info(
            f"{i18n.t('general.book')} {i18n.t('general.exported')} {i18n.t('general.to_excel')}",
            True,
        )


@click.command()
def new():
    """Create a new Book in DATA_PATH, see `bankr.yaml`.

    Creates an almost empty Book, which contains a zero value "Initial Transaction" for each
    account in `accounts.yaml`.
    """
    _bankr_title("New Book Mode")
    bf.create_new_book(data_path)
    _bankr_info("New Book created! Return to a backup, if processed erroneously.", True)
