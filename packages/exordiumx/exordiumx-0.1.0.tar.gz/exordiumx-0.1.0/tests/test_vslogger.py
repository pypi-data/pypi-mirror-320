import unittest
from unittest.mock import patch
from io import StringIO
import sys
from exordiumx import get_logger

class TestVSCodeLogger(unittest.TestCase):
    def setUp(self):
        self.logger = get_logger("test_logger")

    def test_logger_creation(self):
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.name, "test_logger")

    @patch('sys.stderr', new_callable=StringIO)
    def test_info_log(self, mock_stdout):
        self.logger.info("Test info message")
        log_output = mock_stdout.getvalue()
        self.assertIn("INFO", log_output)
        self.assertIn("Test info message", log_output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_debug_log(self, mock_stdout):
        self.logger.debug("Test debug message")
        log_output = mock_stdout.getvalue()
        self.assertIn("DEBUG", log_output)
        self.assertIn("Test debug message", log_output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_warning_log(self, mock_stdout):
        self.logger.warning("Test warning message")
        log_output = mock_stdout.getvalue()
        self.assertIn("WARNING", log_output)
        self.assertIn("Test warning message", log_output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_success_log(self, mock_stdout):
        self.logger.success("Test success message")
        log_output = mock_stdout.getvalue()
        self.assertIn("SUCCESS", log_output)
        self.assertIn("Test success message", log_output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_error_log(self, mock_stdout):
        self.logger.error("Test error message")
        log_output = mock_stdout.getvalue()
        self.assertIn("ERROR", log_output)
        self.assertIn("Test error message", log_output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_critical_log(self, mock_stdout):
        self.logger.critical("Test critical message")
        log_output = mock_stdout.getvalue()
        self.assertIn("CRITICAL", log_output)
        self.assertIn("Test critical message", log_output)

if __name__ == '__main__':
    unittest.main()