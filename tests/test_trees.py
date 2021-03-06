from __future__ import absolute_import

import unittest
from unittest import TestCase
import copy
import pickle

from lark.tree import Tree
from lark.visitors import Transformer, Interpreter, visit_children_decor, v_args


class TestTrees(TestCase):
    def setUp(self):
        self.tree1 = Tree('a', [Tree(x, y) for x, y in zip('bcd', 'xyz')])

    def test_deepcopy(self):
        assert self.tree1 == copy.deepcopy(self.tree1)

    def test_pickle(self):
        s = copy.deepcopy(self.tree1)
        data = pickle.dumps(s)
        assert pickle.loads(data) == s


    def test_interp(self):
        t = Tree('a', [Tree('b', []), Tree('c', []), 'd'])

        class Interp1(Interpreter):
            def a(self, tree):
                return self.visit_children(tree) + ['e']

            def b(self, tree):
                return 'B'

            def c(self, tree):
                return 'C'

        self.assertEqual(Interp1().visit(t), list('BCde'))

        class Interp2(Interpreter):
            @visit_children_decor
            def a(self, values):
                return values + ['e']

            def b(self, tree):
                return 'B'

            def c(self, tree):
                return 'C'

        self.assertEqual(Interp2().visit(t), list('BCde'))

        class Interp3(Interpreter):
            def b(self, tree):
                return 'B'

            def c(self, tree):
                return 'C'

        self.assertEqual(Interp3().visit(t), list('BCd'))

    def test_transformer(self):
        t = Tree('add', [Tree('sub', [Tree('i', ['3']), Tree('f', ['1.1'])]), Tree('i', ['1'])])

        class T(Transformer):
            i = v_args(inline=True)(int)
            f = v_args(inline=True)(float)

            sub = lambda self, values: values[0] - values[1]

            def add(self, values):
                return sum(values)

        res = T().transform(t)
        self.assertEqual(res, 2.9)

        @v_args(inline=True)
        class T(Transformer):
            i = int
            f = float
            sub = lambda self, a, b: a-b

            def add(self, a, b):
                return a + b


        res = T().transform(t)
        self.assertEqual(res, 2.9)


        @v_args(inline=True)
        class T(Transformer):
            i = int
            f = float
            from operator import sub, add

        res = T().transform(t)
        self.assertEqual(res, 2.9)



if __name__ == '__main__':
    unittest.main()

