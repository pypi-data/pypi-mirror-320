import textok
from textok import version

class TestClass:
    def test_version(self):
        assert textok.__version__ == version.__version__
