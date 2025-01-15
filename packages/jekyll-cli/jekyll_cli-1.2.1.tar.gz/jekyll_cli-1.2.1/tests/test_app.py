# -*- coding: UTF-8 -*-
from typer.testing import CliRunner

from jekyll_cli import app

runner = CliRunner()


def test_main():
    result = runner.invoke(app)
    assert result.exit_code == 0


def test_list():
    result = runner.invoke(app, 'list')
    assert result.exit_code == 0
