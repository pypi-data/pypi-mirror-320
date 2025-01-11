# Best Practices

## The Raw CSV Data

* The CSV exports of a bank's web account tends to be quite stable, however, updates of the web access typically go along with a change of the CSV file format.
* The CSV files `<IBAN>-<DATE>.csv` are marked with the date of the download in the format `YYYYmmdd`. CSV files are expected within the subfolder `csv`.
* When downloading from the web access, it is good practice to use the time interval from the last download date until yesterday, and set the new date to today. This avoids the risk of losing Transactions from today.
* `bankr parse <IBAN>-<DATE>.csv` displays some statistics, especially the updated account balance, to check if all Transactions were found and sum up correctly.
* To start an already exsting bank account in *Bankr*, it is straight forward to create a CSV with an »initial transaction«, which represents the account balance at the start of the data import. A new Book might already contain such a transaction with zero value, which you can edit easily.
* CSV downloads of most of my banks are quite reasonable, however, some oddities might occur. The ones I am aware of, are:
    - The value of a transaction can be a quite pathological string, although most currencies nowadays should be given in the form `*.??` (cents and major currency units like €). Please see the function `to_cents` for acceptable strings, and how they are interpreted.
    - Normally, the balance of the account is useful to track the completeness of the transactions. However, a bank might give the balance at the time of the download, and not at the end of the requested interval. Very useful...
    - Transactions can be in prebook state, and might be implemented in CSVs. There seems to be no agreement of banks how to treat these in exports, and erroneous double booking might be possible.


## The Book

* The data format of the Book is given in `book-v1.yaml`. Please consider the comments there, if you plan to change its data format.
* As soon as the Book is updated, it creates a new `book-v1.pickle` in the data folder after saving a backup. Please read the documentation of Pandas or Python to understand, what a pickle of a DataFrame (or any other Python data structure) is.
* Although a pickle is a binary format, it is **NOT** encrypted. Use a folder or a disk based encryption method to be save. *Bankr* will never implement any cryptography to secure its data!


## The Pages & Conditioning

* Pages are a conditioned version of raw CSV Transactions.
* Conditioning resorts and reformats the columns of the raw CSV import in accordance with the Book.


## The YAML Configurations

* The [YAML](https://yaml.org/) configuration file format is simple in structure. However, encoding might be an issue.
* Please seek advice from the [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) for special characters, or use PyYAML's `yaml.dump` functionality, if in doubt.
