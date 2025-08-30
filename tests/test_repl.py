"""Tests for the ChronoStack REPL."""

import io
import unittest
from unittest.mock import patch

from chronostack.repl import ChronoStackREPL


class TestREPL(unittest.TestCase):
    """Test REPL functionality."""

    def setUp(self):
        """Set up test REPL."""
        self.repl = ChronoStackREPL()

    def test_repl_initialization(self):
        """Test REPL initializes correctly."""
        assert self.repl.interpreter is not None
        assert self.repl.interpreter.current_stack() == []

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_basic_arithmetic(self, mock_stdout, mock_input):
        """Test basic arithmetic in REPL."""
        mock_input.side_effect = ["5 3 +", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "[8]" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_stack_command(self, mock_stdout, mock_input):
        """Test .stack command."""
        mock_input.side_effect = ['42 "hello"', ".stack", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert '[42, "hello"]' in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_timeline_command(self, mock_stdout, mock_input):
        """Test .timeline command."""
        mock_input.side_effect = ["42 tick", ".timeline", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Timeline" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_moment_command(self, mock_stdout, mock_input):
        """Test .moment command."""
        mock_input.side_effect = ["42 tick", ".moment", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Current moment:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_branches_command(self, mock_stdout, mock_input):
        """Test .branches command."""
        mock_input.side_effect = ['"test" branch', ".branches", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Branches:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_words_command(self, mock_stdout, mock_input):
        """Test .words command."""
        mock_input.side_effect = [":double dup + ;", ".words", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "double" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_help_command(self, mock_stdout, mock_input):
        """Test .help command."""
        mock_input.side_effect = [".help", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Available commands:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_clear_command(self, mock_stdout, mock_input):
        """Test .clear command."""
        mock_input.side_effect = ["1 2 3", ".clear", ".stack", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "[]" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_reset_command(self, mock_stdout, mock_input):
        """Test .reset command."""
        mock_input.side_effect = [":test 42 ;", "5 tick", ".reset", ".moment", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Current moment: 0" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_parse_error_handling(self, mock_stdout, mock_input):
        """Test parse error handling."""
        mock_input.side_effect = ["[ unclosed", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Parse error:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_runtime_error_handling(self, mock_stdout, mock_input):
        """Test runtime error handling."""
        mock_input.side_effect = ["0 0 /", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Runtime error:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_empty_input(self, mock_stdout, mock_input):
        """Test empty input handling."""
        mock_input.side_effect = ["", "exit"]

        self.repl.run()

        # Should not crash

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_whitespace_input(self, mock_stdout, mock_input):
        """Test whitespace-only input."""
        mock_input.side_effect = ["   \n  ", "exit"]

        self.repl.run()

        # Should not crash

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_unknown_command(self, mock_stdout, mock_input):
        """Test unknown debug command."""
        mock_input.side_effect = [".unknown", "exit"]

        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Unknown command:" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_keyboard_interrupt(self, mock_stdout, mock_input):
        """Test keyboard interrupt handling."""
        mock_input.side_effect = KeyboardInterrupt()

        # Should exit gracefully
        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Goodbye!" in output

    @patch("builtins.input")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_eof_error(self, mock_stdout, mock_input):
        """Test EOF error handling."""
        mock_input.side_effect = EOFError()

        # Should exit gracefully
        self.repl.run()

        output = mock_stdout.getvalue()
        assert "Goodbye!" in output


if __name__ == "__main__":
    unittest.main()
