# -*- coding: utf-8  -*-
#
# Copyright (C) 2012-2013 Ben Kurtovic <ben.kurtovic@verizon.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals
import unittest

from mwparserfromhell.nodes import (Argument, Comment, Heading, HTMLEntity,
                                    Tag, Template, Text, Wikilink)
from mwparserfromhell.smart_list import SmartList
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell import parse
from mwparserfromhell.compat import str

from ._test_tree_equality import TreeEqualityTestCase, wrap, wraptext

class TestWikicode(TreeEqualityTestCase):
    """Tests for the Wikicode class, which manages a list of nodes."""

    def test_unicode(self):
        """test Wikicode.__unicode__()"""
        code1 = parse("foobar")
        code2 = parse("Have a {{template}} and a [[page|link]]")
        self.assertEqual("foobar", str(code1))
        self.assertEqual("Have a {{template}} and a [[page|link]]", str(code2))

    def test_nodes(self):
        """test getter/setter for the nodes attribute"""
        code = parse("Have a {{template}}")
        self.assertEqual(["Have a ", "{{template}}"], code.nodes)
        L1 = SmartList([Text("foobar"), Template(wraptext("abc"))])
        L2 = [Text("barfoo"), Template(wraptext("cba"))]
        L3 = "abc{{def}}"
        code.nodes = L1
        self.assertIs(L1, code.nodes)
        code.nodes = L2
        self.assertIs(L2, code.nodes)
        code.nodes = L3
        self.assertEqual(["abc", "{{def}}"], code.nodes)
        self.assertRaises(ValueError, setattr, code, "nodes", object)

    def test_get(self):
        """test Wikicode.get()"""
        code = parse("Have a {{template}} and a [[page|link]]")
        self.assertIs(code.nodes[0], code.get(0))
        self.assertIs(code.nodes[2], code.get(2))
        self.assertRaises(IndexError, code.get, 4)

    def test_set(self):
        """test Wikicode.set()"""
        code = parse("Have a {{template}} and a [[page|link]]")
        code.set(1, "{{{argument}}}")
        self.assertEqual("Have a {{{argument}}} and a [[page|link]]", code)
        self.assertIsInstance(code.get(1), Argument)
        code.set(2, None)
        self.assertEqual("Have a {{{argument}}}[[page|link]]", code)
        code.set(-3, "This is an ")
        self.assertEqual("This is an {{{argument}}}[[page|link]]", code)
        self.assertRaises(ValueError, code.set, 1, "foo {{bar}}")
        self.assertRaises(IndexError, code.set, 3, "{{baz}}")
        self.assertRaises(IndexError, code.set, -4, "{{baz}}")

    def test_index(self):
        """test Wikicode.index()"""
        code = parse("Have a {{template}} and a [[page|link]]")
        self.assertEqual(0, code.index("Have a "))
        self.assertEqual(3, code.index("[[page|link]]"))
        self.assertEqual(1, code.index(code.get(1)))
        self.assertRaises(ValueError, code.index, "foo")

        code = parse("{{foo}}{{bar|{{baz}}}}")
        self.assertEqual(1, code.index("{{bar|{{baz}}}}"))
        self.assertEqual(1, code.index("{{baz}}", recursive=True))
        self.assertEqual(1, code.index(code.get(1).get(1).value,
                                       recursive=True))
        self.assertRaises(ValueError, code.index, "{{baz}}", recursive=False)
        self.assertRaises(ValueError, code.index,
                          code.get(1).get(1).value, recursive=False)

    def test_insert(self):
        """test Wikicode.insert()"""
        code = parse("Have a {{template}} and a [[page|link]]")
        code.insert(1, "{{{argument}}}")
        self.assertEqual(
            "Have a {{{argument}}}{{template}} and a [[page|link]]", code)
        self.assertIsInstance(code.get(1), Argument)
        code.insert(2, None)
        self.assertEqual(
            "Have a {{{argument}}}{{template}} and a [[page|link]]", code)
        code.insert(-3, Text("foo"))
        self.assertEqual(
            "Have a {{{argument}}}foo{{template}} and a [[page|link]]", code)

        code2 = parse("{{foo}}{{bar}}{{baz}}")
        code2.insert(1, "abc{{def}}ghi[[jk]]")
        self.assertEqual("{{foo}}abc{{def}}ghi[[jk]]{{bar}}{{baz}}", code2)
        self.assertEqual(["{{foo}}", "abc", "{{def}}", "ghi", "[[jk]]",
                          "{{bar}}", "{{baz}}"], code2.nodes)

        code3 = parse("{{foo}}bar")
        code3.insert(1000, "[[baz]]")
        code3.insert(-1000, "derp")
        self.assertEqual("derp{{foo}}bar[[baz]]", code3)

    def test_insert_before(self):
        """test Wikicode.insert_before()"""
        code = parse("{{a}}{{b}}{{c}}{{d}}")
        code.insert_before("{{b}}", "x", recursive=True)
        code.insert_before("{{d}}", "[[y]]", recursive=False)
        self.assertEqual("{{a}}x{{b}}{{c}}[[y]]{{d}}", code)
        code.insert_before(code.get(2), "z")
        self.assertEqual("{{a}}xz{{b}}{{c}}[[y]]{{d}}", code)
        self.assertRaises(ValueError, code.insert_before, "{{r}}", "n",
                          recursive=True)
        self.assertRaises(ValueError, code.insert_before, "{{r}}", "n",
                          recursive=False)

        code2 = parse("{{a|{{b}}|{{c|d={{f}}}}}}")
        code2.insert_before(code2.get(0).params[0].value.get(0), "x",
                            recursive=True)
        code2.insert_before("{{f}}", "y", recursive=True)
        self.assertEqual("{{a|x{{b}}|{{c|d=y{{f}}}}}}", code2)
        self.assertRaises(ValueError, code2.insert_before, "{{f}}", "y",
                          recursive=False)

    def test_insert_after(self):
        """test Wikicode.insert_after()"""
        code = parse("{{a}}{{b}}{{c}}{{d}}")
        code.insert_after("{{b}}", "x", recursive=True)
        code.insert_after("{{d}}", "[[y]]", recursive=False)
        self.assertEqual("{{a}}{{b}}x{{c}}{{d}}[[y]]", code)
        code.insert_after(code.get(2), "z")
        self.assertEqual("{{a}}{{b}}xz{{c}}{{d}}[[y]]", code)
        self.assertRaises(ValueError, code.insert_after, "{{r}}", "n",
                          recursive=True)
        self.assertRaises(ValueError, code.insert_after, "{{r}}", "n",
                          recursive=False)

        code2 = parse("{{a|{{b}}|{{c|d={{f}}}}}}")
        code2.insert_after(code2.get(0).params[0].value.get(0), "x",
                           recursive=True)
        code2.insert_after("{{f}}", "y", recursive=True)
        self.assertEqual("{{a|{{b}}x|{{c|d={{f}}y}}}}", code2)
        self.assertRaises(ValueError, code2.insert_after, "{{f}}", "y",
                          recursive=False)

    def test_replace(self):
        """test Wikicode.replace()"""
        code = parse("{{a}}{{b}}{{c}}{{d}}")
        code.replace("{{b}}", "x", recursive=True)
        code.replace("{{d}}", "[[y]]", recursive=False)
        self.assertEqual("{{a}}x{{c}}[[y]]", code)
        code.replace(code.get(1), "z")
        self.assertEqual("{{a}}z{{c}}[[y]]", code)
        self.assertRaises(ValueError, code.replace, "{{r}}", "n",
                          recursive=True)
        self.assertRaises(ValueError, code.replace, "{{r}}", "n",
                          recursive=False)

        code2 = parse("{{a|{{b}}|{{c|d={{f}}}}}}")
        code2.replace(code2.get(0).params[0].value.get(0), "x", recursive=True)
        code2.replace("{{f}}", "y", recursive=True)
        self.assertEqual("{{a|x|{{c|d=y}}}}", code2)
        self.assertRaises(ValueError, code2.replace, "y", "z", recursive=False)

    def test_append(self):
        """test Wikicode.append()"""
        code = parse("Have a {{template}}")
        code.append("{{{argument}}}")
        self.assertEqual("Have a {{template}}{{{argument}}}", code)
        self.assertIsInstance(code.get(2), Argument)
        code.append(None)
        self.assertEqual("Have a {{template}}{{{argument}}}", code)
        code.append(Text(" foo"))
        self.assertEqual("Have a {{template}}{{{argument}}} foo", code)
        self.assertRaises(ValueError, code.append, slice(0, 1))

    def test_remove(self):
        """test Wikicode.remove()"""
        code = parse("{{a}}{{b}}{{c}}{{d}}")
        code.remove("{{b}}", recursive=True)
        code.remove(code.get(1), recursive=True)
        self.assertEqual("{{a}}{{d}}", code)
        self.assertRaises(ValueError, code.remove, "{{r}}", recursive=True)
        self.assertRaises(ValueError, code.remove, "{{r}}", recursive=False)

        code2 = parse("{{a|{{b}}|{{c|d={{f}}{{h}}}}}}")
        code2.remove(code2.get(0).params[0].value.get(0), recursive=True)
        code2.remove("{{f}}", recursive=True)
        self.assertEqual("{{a||{{c|d={{h}}}}}}", code2)
        self.assertRaises(ValueError, code2.remove, "{{h}}", recursive=False)

    def test_filter_family(self):
        """test the Wikicode.i?filter() family of functions"""
        pass

    def test_get_sections(self):
        """test Wikicode.get_sections()"""
        pass

    def test_strip_code(self):
        """test Wikicode.strip_code()"""
        pass

    def test_get_tree(self):
        """test Wikicode.get_tree()"""
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)