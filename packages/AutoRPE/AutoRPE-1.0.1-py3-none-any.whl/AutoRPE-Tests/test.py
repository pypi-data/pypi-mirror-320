import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir='.', pattern="Test*.py")
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)
