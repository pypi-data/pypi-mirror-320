import unittest
from boudy_toolkit import (
    Theme,
    initialize,
    create_form,
    cpu_usage,
    get_public_ip,
    Validator
)

class TestToolkit(unittest.TestCase):
    def test_theme_values(self):
        self.assertIsInstance(Theme.DARK, dict)
        self.assertIn('bg', Theme.DARK)
        self.assertIn('fg', Theme.DARK)
        
    def test_validator(self):
        validator = Validator()
        self.assertTrue(validator.is_email("test@example.com"))
        self.assertFalse(validator.is_email("invalid-email"))
        
        self.assertTrue(validator.is_phone("+1234567890"))
        self.assertFalse(validator.is_phone("abc"))
        
        self.assertTrue(validator.is_date("2024-01-14"))
        self.assertFalse(validator.is_date("invalid-date"))

if __name__ == '__main__':
    unittest.main()