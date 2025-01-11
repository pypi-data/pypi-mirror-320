# Bankr

[![PyPI - Version](https://img.shields.io/pypi/v/bankr.svg)](https://pypi.org/project/bankr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bankr.svg)](https://pypi.org/project/bankr)

-----

*Bankr is simple Python for your Bank Accounting to categorize your incomes and expenses*


## About

*Bankr*…

- …collects all your bank transactions on your chart of accounts using a CLI. The collection of the transactions is performed via CSV export from your bank accounts.
- …categorizes the transactions using a simple filter mechanism for repeating bookings. One-time transactions can be categorized by hand.
- …allows to add, edit and delete bank transactions by hand.
- …and finally, shows plots and statistics on the Book within the CLI or your web browser.
- …is configured via small and human-readable YAML files, which you can modify using any editor.
- …and, hopefully, creates an overview over your finances.

---

***Alpha** Software*

This software is in **Alpha** state. There are a several TODOs in the source code, and some further limitations to remove for completion of its functionality! However, `v1` of the data format should be stable right now.

---


## Motivation

My motivation for writing these lines of Python code are two-fold:

1. Learning *Python*, *Pandas*, and - currently at very basic level in this Python project - *Panel*.
2. Starting with CSV based accounting, especially after some negative experiences with trying to use an [HBCI (now FinTS)](https://en.wikipedia.org/wiki/FinTS) based accounting system. At least in Germany, banks tend to break their own HBCI accesses, especially since their most important accesses seem to be their own and individual banking apps. Fortunately, I am not aware of a bank, which does not allow a CSV based download of the respective transaction data.


## Installation

Install `python` and `pip` for your system, and do the following installation into a virtual environment `bankr`:

```console
python -m venv bankr
cd bankr
pip install bankr
```

*Bankr* includes fictional sample data in `bankr/data.sample` and a sample config file `bankr/bankr.sample.yaml`. Linking to the folder and the config file from your working directory, having the virtual environment activated, should allow to run Bankr on this sample data:

```console
ln -s <path/to/bankr/bankr.sample.yaml> bankr.yaml
ln -s <path/to/bankr/data.sample> data
```

Check the consistency of your configuration, and give it a try: `bankr stats`. If you see a big *Bankr* headline and a table of four "fantastic" bank accounts, you are in.

---

**Note** *Bankr* is tested on Linux only right now. Give it a try on BSD, Windows or Mac. I would not expect any hickups, but be prepared. You are heartily invited to provide feedback.

---


## Documentation

*Bankr* is fully documented [here](https://rokor.codeberg.page/bankr).


## License

*Bankr* is distributed under the terms of the [Unlicense](https://spdx.org/licenses/Unlicense.html) license.
