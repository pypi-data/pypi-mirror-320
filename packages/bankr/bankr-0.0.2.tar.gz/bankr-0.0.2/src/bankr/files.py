"""*Bankr* module for parsing of CSVs or Pages, and other file operations."""

import sys

import yaml
import pandas as pd
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import inquirer as iq
from schwifty import IBAN

import bankr.calc as bc


# Helper - Create an UUID
def _create_uuid(x: str) -> str:
    return uuid.uuid4()


# Helper - Remove unnecessary spaces in desc
def _remove_spaces(x: str) -> str:
    return " ".join(x.split())


# Read parameters


def read_bankr_yaml(path: Path) -> dict:
    """Read parameters from YAML file format."""
    try:
        with open(path, "r") as file:
            bankr_yaml = yaml.safe_load(file)
        return bankr_yaml
    except FileNotFoundError as e:
        sys.exit(f"Bankr Error - YAML file not found.\n{e}")


# Parsing CSVs from banks


def parse_csv(path: Path, csv_file: str) -> pd.DataFrame:
    """Parse CSV and create a Page.

    Parse the CSV, defined by `<bank_code>.yaml`, and condition the parsed data.
    """
    # TODO The dtypes of the Pages returned from `parse_csv` and `create_transaction` are inconsistent.
    # Check IBAN
    iban = csv_file.split("-")[0]
    source = csv_file.replace(".", "-").split("-")[1]
    if not IBAN(iban).is_valid:
        sys.exit("Bankr Error - Filename contains invalid IBAN")

    # Get CSV format dictionary from JSON
    csv_format_path = path / ("csv/" + IBAN(iban).bank_code + ".yaml")
    csv_format = read_bankr_yaml(csv_format_path)

    # Read CSV and add missing data series
    csv_path = path / ("csv/" + csv_file)
    try:
        csv = pd.read_csv(
            csv_path,
            sep=csv_format["sep"],
            encoding=csv_format["encoding"],
            dtype="string",
            skiprows=csv_format["skiprows"],
            header=0,
            index_col=False,
            names=csv_format["names"],
        )
    except BaseException as e:  # Catch all exceptions
        sys.exit(f"Bankr Error - Page could not be read from CSV.\n{e}")

    # Create Transaction IDs
    csv["uuid"] = [uuid.uuid4() for _ in range(csv.shape[0])]
    csv.uuid = csv.uuid.astype("string")
    csv.set_index("uuid", inplace=True)

    # Create cents - tricky operation, see documentation
    csv.cents = csv.cents.apply(to_cents).astype("string")
    csv["iban"] = iban
    csv.iban = csv.iban.astype("string")
    csv["source"] = source
    csv["source"] = csv["source"].astype("string")
    missing = csv_format["missing"]
    for key in missing:
        csv[key] = missing[key]
        csv[key] = csv[key].astype("string")
    page = condition_book(csv, path, csv_format["dateformat"])

    return page


def to_cents(x: str) -> str:
    """Filter an "amount of money" string in a CSV.

    Strings indicating a certain amount of money can be quite pathological in CSV files of banks.
    Therefore, these need to be filtered, before being converted to integers:
    1. Limit to acceptable characters `"0123456789.,+- "`.
    2. Only dots as separators of cents and thousands.
    3. "" and "-" give "0".
    4. Minus sign as first character, no plus sign.

    "000" can happen as filter result, but this is fine for integers.
    """
    accept = set("0123456789.,+- ")
    check = set(x)
    if not check.issubset(accept):
        return "0"
    x = x.replace(",", ".").replace("+", "").replace(" ", "")
    if "-" in x:
        x = "-" + x.replace("-", "")
    if len(x) == 0 or x == "-":
        return "0"

    # Normal cases: *.??
    if len(x) > 2 and x[-3] == ".":
        return x.replace(".", "")

    # Pathological cases
    x = x + "00"
    if len(x) == 3:
        return x  # Single digit
    if len(x) >= 4:
        if x[-4] == ".":
            x = x[:-1]  # One digit after separator
        return x.replace(".", "")


# Creating a transaction, value checks


def create_transaction(iban: str) -> pd.DataFrame:
    """Create a Page with one Transaction interactively."""
    # TODO The dtypes of the Pages returned from `parse_csv` and `create_transaction` are inconsistent.
    # TODO Offer cat with choices.
    # TODO Select today, if date/valuta is invalid. Accept empty date strings.
    ask = [
        iq.Text("date", message="Date (dd.mm.YYYY)", validate=_validate_date),
        iq.List("curr", message="Currency", choices=["€", "$"], default="€"),
        iq.Text("cents", message="Value ({curr})"),
        iq.Text("cat", message="Category"),
        iq.Text("valuta", message="Valuta (dd.mm.YYYY)"),
        iq.Text("offset", message="Offset (Empty, or IBAN)", validate=_validate_iban),
        iq.Text("name", message="Account holder (*)"),
        iq.Text("process", message="Process (*)"),
        iq.Text("desc", message="Description (*)"),
        iq.Text("creditor", message="Creditor ID (*)"),
        iq.Text("mandate", message="Mandate Reference (*)"),
        iq.Text("customer", message="Customer Reference (*)"),
    ]
    tract = iq.prompt(ask)
    page = pd.DataFrame({key: [value] for key, value in tract.items()})
    page["cents"] = page["cents"].apply(to_cents)
    page["iban"] = iban
    page["uuid"] = uuid.uuid4()
    page["source"] = "interactive"
    page = page.astype("string")

    return page


def edit_transaction(tract: pd.Series) -> pd.Series:
    """Edit a Transaction."""
    tract = tract.fillna("")  # <NA> not allowed as default
    uuid = tract.name
    iban = tract["iban"]
    source = tract["source"]
    ask = [
        iq.Text(
            "date", message="Date (dd.mm.YYYY)", validate=_validate_date, default=tract["date"].strftime("%d.%m.%Y")
        ),
        iq.List("curr", message="Currency", choices=["€", "$"], default=tract["curr"]),
        iq.Text("cents", message="Value ({curr})", default=f"{tract["cents"] / 100 : >10.2f}"),
        iq.Text("cat", message="Category", default=tract["cat"]),
        iq.Text("valuta", message="Valuta (dd.mm.YYYY)", default=tract["date"].strftime("%d.%m.%Y")),
        iq.Text("offset", message="Offset (Empty, or IBAN)", validate=_validate_iban, default=tract["offset"]),
        iq.Text("name", message="Account holder (*)", default=tract["name"]),
        iq.Text("process", message="Process (*)", default=tract["process"]),
        iq.Text("desc", message="Description (*)", default=tract["desc"]),
        iq.Text("creditor", message="Creditor ID (*)", default=tract["creditor"]),
        iq.Text("mandate", message="Mandate Reference (*)", default=tract["mandate"]),
        iq.Text("customer", message="Customer Reference (*)", default=tract["customer"]),
    ]
    editions = iq.prompt(ask)
    tract = pd.Series(editions)
    tract["date"] = datetime.strptime(tract["date"], "%d.%m.%Y")
    tract["valuta"] = datetime.strptime(tract["valuta"], "%d.%m.%Y")
    tract["cents"] = int(to_cents(tract["cents"]))
    tract["iban"] = iban
    tract.rename(uuid, inplace=True)
    tract["source"] = source + " (edited)"

    return tract


# Helper - Input validation for inquirer
def _validate_iban(tract: list, current: str) -> bool:
    if current == "":
        return True
    else:
        return bc.iban_valid(current)


# Helper - Input validation for inquirer
def _validate_date(tract: list, current: str) -> bool:
    try:
        valid = bool(datetime.strptime(current, "%d.%m.%Y"))
    except ValueError:
        valid = False
    return valid


# Manipulation of the Book


def pickle_book(book: pd.DataFrame, path: Path) -> None:
    """Save the Book as `book-v1.pickle` in `path`.

    If an Excel version of the Book is present under `xlsx`, do not pickle.
    Backup the old `book-v1.pickle` as `book-v1_<datetime>.pickle`, before pickling a new version.
    """
    # No pickle, if XLSX version is present
    if (path / "xlsx" / "book-v1.xlsx").is_file():
        sys.exit("Bankr Error -  Excel version present. Book could not be saved.")

    # Create backup
    pickle_path = path / "book-v1.pickle"
    if (pickle_path).is_file():
        pickle_path.rename(path / ("book-v1_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".pickle"))

    # And create "book-v1.pickle"
    try:
        book.to_pickle(pickle_path)
    except RuntimeError as e:
        sys.exit(f"Bankr Error - Book could not be saved.\n{e}")


def unpickle_book(path: Path) -> pd.DataFrame:
    """Read the Book from `book-v1.pickle` in `path`.

    Raise error, if the pickled Book is not found.
    """
    try:
        book = pd.read_pickle(path / "book-v1.pickle")
        return book
    except FileNotFoundError as e:
        sys.exit(f"Bankr Error - Book not found.\n{e}")


def create_new_book(data_path: Path) -> None:
    """Create new Book.

    Creates an almost empty book, which contains zero value "Initial Transaction" for each
    account in `accounts.yaml`. The path to be used is taken from `bankr.yaml`. If an existing
    Book is overwritten accidentially, use the backup file, see the documentation.
    """
    book_format = read_bankr_yaml(data_path / "book-v1.yaml")
    accounts = read_bankr_yaml(data_path / "accounts.yaml")

    tracts = len(accounts)

    yesterday = datetime.today() - timedelta(days=1)
    date_values = [yesterday.strftime("%d.%m.%Y")] * tracts
    iban_values = []
    for n in range(tracts):
        iban_values.append(accounts[n]["iban"])
    cents_values = [0] * tracts
    curr_values = ["€"] * tracts
    cat_values = ["none"] * tracts
    desc_values = ["Initial Transaction"] * tracts
    source_values = ["initial"] * tracts
    empty_values = [""] * tracts

    book = pd.DataFrame()
    for key in book_format:
        if key == "date" or key == "valuta":
            book[key] = pd.DataFrame(date_values)
        elif key == "iban":
            book[key] = pd.DataFrame(iban_values)
        elif key == "cents":
            book[key] = pd.DataFrame(cents_values)
        elif key == "curr":
            book[key] = pd.DataFrame(curr_values)
        elif key == "cat":
            book[key] = pd.DataFrame(cat_values)
        elif key == "desc":
            book[key] = pd.DataFrame(desc_values)
        elif key == "source":
            book[key] = pd.DataFrame(source_values)
        else:
            book[key] = pd.DataFrame(empty_values)

    book["uuid"] = [uuid.uuid4() for _ in range(tracts)]
    book = book.set_index("uuid")
    book = condition_book(book, data_path, "%d.%m.%Y")
    pickle_book(book, data_path)


def condition_book(book: pd.DataFrame, path: Path, date_format: str) -> pd.DataFrame:
    """Conditioning of a Page or the Book to fit to `book-v1.yaml`.

    Conditioning steps are
    (1) Condition dates to Pandas `datetime64[ns]` (column *date* is mandatory),
    (2) Condition the local IBANs and the *Bankr cat* to Pandas `category`,
    (3) Remove NaNs from `cat`, which are not allowed,
    (4) Remove unnecessary spaces in *desc*.
    """
    book_format = read_bankr_yaml(path / "book-v1.yaml")

    # Condition dates
    for key in book_format:
        if book_format[key] == "datetime64[ns]":
            book[key] = pd.to_datetime(book[key], format=date_format)
        else:
            book[key] = book[key].astype(book_format[key])

    # Condition categoricals to "iban", "cat", and "curr"
    # TODO Check "curr"
    # TODO Take the categoricals from book-v1.yaml
    # k Improve Pandas notation
    accounts = read_bankr_yaml(path / "accounts.yaml")
    iban_list = []
    for account in accounts:
        iban_list.append(account["iban"])
    book.iban = book.iban.cat.set_categories(iban_list)
    cats = read_bankr_yaml(path / "cats.yaml")
    cat_list = []
    for cat in cats:
        cat_list.append(cat["cat"])
    book.cat = book.cat.cat.set_categories(cat_list)

    # Remove NaNs from "cat"
    book["cat"] = book["cat"].fillna(value="none")

    # Replace NAType data with empty strings in string-based columns
    # Remove unnecessary spaces in strings
    for key in book_format:
        if book_format[key] == "string":
            book[key] = book[key].fillna("")
            book[key] = book[key].apply(_remove_spaces).astype(book_format[key])

    # Sort columns
    book = book[[*book_format]]

    return book


# Export and Import of the Book


def excel_book(book: pd.DataFrame, path: Path) -> None:
    """Export the book as `book.xlsx` into `path/xlsx`.

    Do not export, if there is already a `book-v1.xlsx` present.
    *Remark* Function not oerational in v0.0.1 of Bankr.
    """
    # TODO Check if ok with index uuid and source
    xlsx_path = path / "xlsx" / "book-v1.xlsx"
    if (xlsx_path).is_file():
        sys.exit("Bankr Error -  Excel already present. Book was not exported.")
    try:
        book.to_excel(xlsx_path, sheet_name="book", index=False)
    except RuntimeError as e:
        sys.exit(f"Bankr Error - Book could not be exported to Excel.\n{e}")


def unexcel_book(path: Path) -> pd.DataFrame:
    """Import the Book from `xlsx/book.xlsx` and rename the Excel file.

    We make a backup from `book-v1.xlsx` as `book-v1-<datetime>.xlsx`.
    *Remark* Function not oerational in v0.0.1 of Bankr.
    """
    # TODO Check if ok with index uuid and source
    xlsx_path = path / "xlsx" / "book-v1.xlsx"
    try:
        book = pd.read_excel(xlsx_path, sheet_name="book", index_col=None)
        book = condition_book(book, path, "%d.%m.%Y")
    except FileNotFoundError as e:
        sys.exit(f"Bankr Error - Book could not be imported from Excel.\n{e}")
    xlsx_path.rename(path / ("xlsx/book-v1_" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx"))
    return book
