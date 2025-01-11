from .builder import LogBuilder

if __name__ == '__main__':
    class TestLogger:

        logger = LogBuilder()\
            .file('test.log')\
            .build(__name__)

        def test(self):
            self.logger.debug("This is a debug message")
            self.logger.info("This is an info message")
            self.logger.warning("This is a warning message")
            self.logger.error("This is an error message")
            self.logger.critical("This is a critical message")

    TestLogger().test()
