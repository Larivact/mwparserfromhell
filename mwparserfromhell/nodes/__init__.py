# -*- coding: utf-8  -*-
#
# Copyright (C) 2012 Ben Kurtovic <ben.kurtovic@verizon.net>
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

from mwparserfromhell.string_mixin import StringMixIn

__all__ = ["Node"]

class Node(StringMixIn):
    def __iternodes__(self, getter):
        yield None, self

    def __strip__(self, normalize, collapse):
        return None

from mwparserfromhell.nodes import extras
from mwparserfromhell.nodes.text import Text
from mwparserfromhell.nodes.heading import Heading
from mwparserfromhell.nodes.html_entity import HTMLEntity
from mwparserfromhell.nodes.tag import Tag
from mwparserfromhell.nodes.template import Template