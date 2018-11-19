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
    name: /\w+/
    
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
        self.fcount[self.curr]["up"] = self.fcount[self.curr]["up"] - 1
        self.fcount[self.curr]["down"] = self.fcount[self.curr]["down"] + 1

    def name(self, s):
        feature = s[0].value
        self.curr = feature
        if not feature in self.fcount:
            self.fcount[feature] = {"up": 0, "down": 0}

        self.fcount[feature]["up"] = self.fcount[feature]["up"] + 1
