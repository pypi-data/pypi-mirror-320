# Technical Implementation

## General Remarks

As mentioned in the title, *Bankr* itself is simple and functional Python. The heavy lifting for the transaction data is done using [Pandas](https://pandas.pydata.org/) DataFrames. However, since manipulations of *Series* and *DataFrames* within Pandas can be quite tricky, its major building blocks are explained here.

A CLI based command typically consists of a series of data manipulations or Python functions, as can be seen in the section [The Command Line Interface](reference.md#the-command-line-interface) within the [Reference](reference.md). It is therefore straight forward to do individual data manipulations using the [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) of Python or [IPython](https://ipython.readthedocs.io/en/stable/). A modification of the Book's data format for example would consist of the following data manipulation steps:

- Unpickle the Book in Python or IPython
- Change the format of the Book as desired
- Pickle the Book
- Adapt `book-v1.yaml` accordingly

Further manipulations of the Book can be done again using the CLI commands.


## Data Structure

*Bankr* gets its configuration from `./bankr.yaml` in the starting folder, and saves its data within a further data folder, which is defined in `bankr.yaml`. As a YAML file, it is human-readable in any editor. Further YAMLs, see below, define the data structure. These files are commented, so please see the infos there. Furthermore, *Bankr* never writes any `*.yaml` config files, but saves only data by pickling it.

!!! Danger "Only unpickle data with *Bankr*, which was pickled by it!"
    Pickle files are serialized Python data structures. As stated [here](https://docs.python.org/3/library/pickle.html) or [here](https://pymotw.com/3/pickle/), Python's `pickle` module is not secure. Therefore: **Only unpickle data you trust!**

The data structure is as follows:

``` bash
book-v1.pickle              # The Book
book-v1_<DATETIME>.pickle   # Backups of the Book, created at <YYmmdd-HHMMSS>, if present
accounts.yaml               # The accounts, see comments there
book-v1.yaml                # The structure of the Book (of the relevant Pandas DataFrame)
cats.yaml                   # The categories, see comments there
filters.yaml                # The filter information needed for auto categorization
csv/
    <IBAN>-<DATE>.csv       # The Transactions of an IBAN until DATE (Hint: See Best Practices!)
    ...                     # Further IBAN of the same web access of a bank
    <BANK_CODE>.yaml        # The data structure of the bank's web access, defining »their« IBANs
    ...                     # Further pairs of CSVs/BANK_CODE. Bank code as calculated by Schwifty
    zip/                    # Not operational in v0.0.1
        <IBAN>.zip          # Backups of the CSVs per IBAN
        <BANK_CODE>.zip     # Backups of the <BANK_CODE>.yaml, if present
xlsx/                       # Excel exports. Not operational in v0.0.1
    book-v1_template.xlsx   # A template for book.xlsx (preliminary)
```

All [YAML](https://yaml.org/) based configuration (*Bankr* uses [PyYAML](https://pyyaml.org/)) is human readable. Adapt these configuration files to your needs in any editor.


## The Book, Pages and Transactions

### The Book

The *Book* is a Pandas DataFrame with columns as defined by `book-v1.yaml`, with respect to column name and data format, as well as the sort order of the columns. It is the only data structure of Bankr, which is saved to and read from disk during normal operations. All other data needed for presentation of the banking data is generated on the fly.

A *Transaction ID* or *UUID* is marking each Transaction. It is generated during the parsing of CSV data, or when adding a Transaction manually. Within the Pandas DataFrame of the Book, it is used as an index.

As seen in the section [Data Structure](implementation.md/#data-structure) above, a backup of the pickled data is generated during pickling of the Book, which is typically the last step in data processing for CLI commands, which change the content of the Book.

The basic data manipulation process is receiving or [parsing](reference.md#src.bankr.files.parse_csv) new data in CSV format from the exports of the bank accounts. When parsing, we generate a *Raw Page* from the CSV, which is similar to a *Page*, but containing the data as strings and potentially having unused columns. After generating an ID for each Transaction within the Raw Page, and calculating the cents of the Transaction, the Raw Page is *conditioned*. This means that the Raw Page is modified having the a.m. format of the Pandas DataFrame. The steps of the data manipulation are described [here](reference.md#src.bankr.files.condition_book).

### Pages

*Pages* are just parts of the *Book* with respect to Transactions, where the Pandas DataFrame of a Page follows the data structure described in `book-v1.yaml`.

Pages typically exist after parsing of CSV, or as a database for the calculation of data to be presented.

### Transactions

A *Transaction* is a Pandas Series of one bank transaction. It follows the data structure given in `book-v1.yaml` within the rows of the Series. The indexes are the keys of `book-v1.yaml`, the name of the Pandas Series is the Transaction ID or UUID.


## Major Data Manipulation

The major data manipulation steps during routine operation of *Bankr* are:

- [Creating](reference.md#src.bankr.files.create_new_book) a new Book: `create_new_book`
- [Parsing CSV](reference.md#src.bankr.files.parse_csv) data from the bank accounts: `parse_csv`
- [Categorizing Transactions manually](reference.md#src.bankr.calc.mancat_tracts), if the filter mechanism is failing: `mancat_tracts`
- Potentially [adding](reference.md#src.bankr.cli.commands.add), [editing](reference.md#src.bankr.cli.commands.edit), or [deleting Transactions](reference.md#src.bankr.cli.commands.delete) in the Book: `*_transaction`

These and all other Python functions are described within the [Reference](reference.md). Major data manipulations under the hood, meaning without a direct CLI command of the user, are:

- [Pickling](reference.md#src.bankr.files.pickle_book) and [unpickling](reference.md#src.bankr.files.unpickle_book) the Book. Not surprising, most CLI commands begin with fetching the Book from disk or unpickling it.
- [Conditioning of Pages](reference.md#src.bankr.files.condition_book) and Transactions. See the [Best Practices](best.md) for more details.
- Auto mode of [categorization](reference.md#src.bankr.calc.autocat_tracts). Typically, this step follows the conditioning for freshly imported Pages.
- Calculation of DataFrames for data presentation (tbc)
