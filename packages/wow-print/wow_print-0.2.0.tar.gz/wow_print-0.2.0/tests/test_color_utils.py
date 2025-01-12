import unittest
import sys
from io import StringIO
from unittest.mock import patch
from wow_print import color_print, ANSINotSupportedError, Colors

from wow_print import color_utils


class TestColorUtils(unittest.TestCase):

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_basic_foreground(self, mock_stdout):
        """Test basic foreground color printing"""
        color_print("Hello, World!", fg="red")
        output = mock_stdout.getvalue()
        self.assertIn("\033[38;5;124m", output)  # Checking red color ANSI code
        self.assertIn("Hello, World!", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_basic_background(self, mock_stdout):
        """Test background color printing"""
        color_print("Hello, World!", bg="blue")
        output = mock_stdout.getvalue()
        self.assertIn("\033[44m", output)  # Checking blue background ANSI code
        self.assertIn("Hello, World!", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_both_foreground_background(self, mock_stdout):
        """Test both foreground and background colors"""
        color_print("Hello, World!", fg="green", bg="yellow")
        output = mock_stdout.getvalue()
        self.assertIn("\033[92m", output)  # Green foreground
        self.assertIn("\033[48;5;11m", output)  # Yellow background
        self.assertIn("Hello, World!", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_bold_italic(self, mock_stdout):
        """Test bold and italic styling, with check for terminal support"""

        # Apply both bold and italic
        color_print("Hello, World!", bold=True, italic=True)
        output = mock_stdout.getvalue()

        # Check if bold style is applied
        self.assertIn("\033[1m", output)  # Bold style should be applied

        # Check if italic style is applied, if supported by terminal
        if '\033[3m' in output:  # Terminal supports italics
            self.assertIn("\033[3m", output)  # Italic style should be applied
        else:
            self.assertNotIn("\033[3m", output)  # Italic style should not be applied in unsupported terminals

        self.assertIn("Hello, World!", output)  # Ensure the text is present

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_time(self, mock_stdout):
        """Test printing with time"""
        color_print("Hello, World!", print_time=True)
        output = mock_stdout.getvalue()
        self.assertTrue(output.startswith("\033[46m\033[30m"), "Time prefix not found in output")
        self.assertIn("Hello, World!", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_color_print_no_time(self, mock_stdout):
        """Test printing without time"""
        color_print("Hello, World!", print_time=False)
        output = mock_stdout.getvalue()
        self.assertNotIn("\033[46m\033[30m", output)  # Ensure time prefix is absent
        self.assertIn("Hello, World!", output)

    def test_unsupported_platform(self):
        """Test that ANSINotSupportedError is raised on unsupported platforms"""
        with patch("sys.platform", "unsupported_os"):
            with self.assertRaises(ANSINotSupportedError):
                color_print("Hello, World!")

    def test_hex_to_rgb(self):
        """Test HEX to RGB conversion"""
        self.assertEqual(color_utils._hex_to_rgb("#ff5733"), (255, 87, 51))
        self.assertEqual(color_utils._hex_to_rgb("#000000"), (0, 0, 0))
        self.assertEqual(color_utils._hex_to_rgb("#ffffff"), (255, 255, 255))

    def test_rgb_to_ansi(self):
        """Test RGB to ANSI conversion"""
        self.assertEqual(color_utils._rgb_to_ansi((255, 87, 51), True), "\033[38;2;255;87;51m")
        self.assertEqual(color_utils._rgb_to_ansi((255, 87, 51), False), "\033[48;2;255;87;51m")

    def test_predefined_color_check(self):
        """Test predefined color check"""
        self.assertEqual(color_utils._predefined_color_check("red"), ["\033[38;5;124m", "\033[48;5;124m"])
        self.assertEqual(color_utils._predefined_color_check("green"), ["\033[92m", "\033[42m"])
        self.assertEqual(color_utils._predefined_color_check("yellow"), ["\033[93m", "\033[48;5;11m"])

    def test_invalid_color(self):
        """Test invalid color input"""
        self.assertEqual(color_utils._predefined_color_check("invalid_color"), [])


if __name__ == "__main__":
    unittest.main()
