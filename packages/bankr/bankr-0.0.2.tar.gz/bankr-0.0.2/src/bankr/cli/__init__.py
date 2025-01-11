# SPDX-FileCopyrightText: 2024-present Robert Kormann <rokor@kormann.info>
#
# SPDX-License-Identifier: Unlicense
import click
import i18n

from pathlib import Path

import bankr.files as bf
import bankr.cli.commands as commands
from bankr.__about__ import __version__

# Debugger
# import bankr.utils as utils

# utils.debugger()

# Init i18n

config_path = Path("./bankr.yaml").resolve()
params = bf.read_bankr_yaml(config_path)
bankr_path = Path(__file__).parent
i18n.set(bankr_path / "locale", params["LOCALE"])
i18n.load_path.append(bankr_path / "locale")


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="bankr")
def bankr():
    pass


# bankr.add_command(commands.test)  # Test command for development
bankr.add_command(commands.new)
bankr.add_command(commands.parse)
bankr.add_command(commands.add)
bankr.add_command(commands.edit)
bankr.add_command(commands.delete)
bankr.add_command(commands.stats)
bankr.add_command(commands.cat)
bankr.add_command(commands.show)
bankr.add_command(commands.plot)
# bankr.add_command(commands.excel)  # TODO Not valid in v0.0.1!
