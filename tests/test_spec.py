import pkg_resources
import os
import unittest

from bundletester import config
from bundletester import spec

TEST_FILES = pkg_resources.resource_filename(__name__, 'files')


def locate(name):
    return os.path.join(TEST_FILES, name)


class TestSpec(unittest.TestCase):

    def test_spec_missing(self):
        self.assertRaises(OSError, spec.Spec, locate('missing'))

    def test_spec_no_config(self):
        test = spec.Spec(locate('test01'))
        self.assertEqual(test.name, os.path.basename(locate('test01')))
        self.assertEqual(test.executable, os.path.abspath(locate('test01')))
        # Verify we got a default config file representation
        self.assertEqual(test.virtualenv, True)

    def test_spec_config(self):
        test = spec.Spec(locate('test02'))
        self.assertEqual(test.name, 'test02')
        self.assertEqual(test.executable, os.path.abspath(locate('test02')))
        # Verify we got a default config file representation
        self.assertEqual(test.setup, ['setup02'])

    def test_spec_config_parent(self):
        parent = config.Parser()
        parent['bootstrap'] = False
        test = spec.Spec(locate('test02'), parent)
        self.assertEqual(test.name, 'test02')
        self.assertEqual(test.executable, os.path.abspath(locate('test02')))
        self.assertEqual(test.setup,  ['setup02'])
        self.assertEqual(test.bootstrap,  False)
        self.assertEqual(test.reset,  False)

    def test_spec_init(self):
        parent = config.Parser()
        parent['bootstrap'] = False
        test = spec.Spec(locate('test02'), parent)
        self.assertEqual(test.name, 'test02')

    def test_suite_spec(self):
        parent = config.Parser()
        parent['bootstrap'] = False
        suite = spec.Suite(parent, None)
        suite.spec(locate('test02'))
        self.assertEqual(suite[0].name, 'test02')
