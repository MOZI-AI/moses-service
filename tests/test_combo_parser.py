__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'
import unittest
from utils.feature_count import combo_parser, ComboTreeTransform


class TestComboParser(unittest.TestCase):

    def setUp(self):
        self.sample_combo = "or(and(or(!$ANK-RD46 $APLN.R) $ARHGAP18) and($APLN.R $ARHGAP18) !$ANK-RD46)"

    def test_tree_transformer(self):
        parse_tree = combo_parser.parse(self.sample_combo)
        tree_transformer = ComboTreeTransform()
        tree_transformer.transform(parse_tree)

        output = {"ANK-RD46": {"case": 0, "control": 2}, "APLN.R": {"case": 2, "control": 0}, "ARHGAP18": {"case": 2, "control": 0}}

        self.assertEqual(tree_transformer.fcount, output)