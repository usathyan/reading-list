"""Tests for CLI functionality."""

import pytest
from click.testing import CliRunner

from reading_list.cli import cli


class TestCLI:
    """Test CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "GitHub Reading List Generator CLI" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_refresh_help(self):
        """Test refresh command help."""
        result = self.runner.invoke(cli, ["refresh", "--help"])
        assert result.exit_code == 0
        assert "Refresh the reading list data" in result.output
    
    def test_export_help(self):
        """Test export command help."""
        result = self.runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0
        assert "Export reading list data" in result.output
    
    def test_init_help(self):
        """Test init command help."""
        result = self.runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize configuration files" in result.output
    
    def test_serve_help(self):
        """Test serve command help."""
        result = self.runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0
        assert "Start the web dashboard" in result.output
    
    def test_status_help(self):
        """Test status command help."""
        result = self.runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "Show current status" in result.output


if __name__ == "__main__":
    pytest.main([__file__]) 