__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'
import unittest
from utils.feature_count import combo_parser, ComboTreeTransform

class TestComboParser(unittest.TestCase):

    def setUp(self):
        self.sample_combo = "or(and(or(!$ANKRD46 $APLNR) $ARHGAP18) and($APLNR $ARHGAP18) !$ANKRD46)"

    def test_tree_transformer(self):
        parse_tree = combo_parser.parse(self.sample_combo)
        tree_transformer = ComboTreeTransform()
        tree_transformer.transform(parse_tree)

        output = {"ANKRD46": {"up": 0, "down": 2}, "APLNR": {"up": 2, "down": 0}, "ARHGAP18": {"up": 2, "down": 0}}

        self.assertEqual(tree_transformer.fcount, output)