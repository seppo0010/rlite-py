import unittest
import sys

# make sure hirlite isn't imported from source
sys.path = sys.path[1:]


def tests():
    from test import rlite, persistent

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(rlite.RliteTest))
    suite.addTest(unittest.makeSuite(persistent.PersistentTest))

    try:
        from test import patch
        suite.addTest(unittest.makeSuite(patch.PatchConnTest))
    except ImportError:
        pass

    return suite
