import unittest


from lei.src.read_lei import read_path

class TestTakePath(unittest.TestCase):

    def test_define_path(self):

        path = read_path.TakePath.define_path()
        assert isinstance(path, str)