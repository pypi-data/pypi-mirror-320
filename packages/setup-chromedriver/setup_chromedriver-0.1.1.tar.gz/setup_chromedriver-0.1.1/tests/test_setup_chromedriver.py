import unittest
from setup_chromedriver.main import get_chrome_version

class TestSetupChromeDriver(unittest.TestCase):
    def test_get_chrome_version(self):
        version = get_chrome_version()
        self.assertIsNotNone(version, "Chrome version should not be None")

if __name__ == "__main__":
    unittest.main()