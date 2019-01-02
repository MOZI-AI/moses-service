__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from lark.tree import Transformer
from lark import Lark


grammar = '''
    combo: func | feature | negate
    func:  and_or lpar param+ rpar
    param: feature | func | negate
    lpar: "("
    rpar: ")"
    and_or: "and" | "or"
    negate: "!" feature
    feature: "$" name
    name: /[^$!()]+/
    
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
'''

combo_parser = Lark(grammar, start='combo', parser='lalr')


class ComboTreeTransform(Transformer):
    """
    This class builds a feature count dictionary by going through a combo tree
    """
    def __init__(self):
        self.fcount = {}
        self.up = True
        self.curr = None

    def negate(self, s):
        self.up = False
        self.fcount[self.curr]["case"] = self.fcount[self.curr]["case"] - 1
        self.fcount[self.curr]["control"] = self.fcount[self.curr]["control"] + 1

    def name(self, s):
        feature = s[0].value.strip()
        self.curr = feature
        if not feature in self.fcount:
            self.fcount[feature] = {"case": 0, "control": 0}

        self.fcount[feature]["case"] = self.fcount[feature]["case"] + 1
