#
# Copyright (c) 2023 Jared Crapo
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""parser classes"""

import contextlib

import rich

from .interpolator import Interpolator


class StyleParser:
    """parse rich.style.Style objects from text or from a dict of texts

    If you pass a dict of styles, those will be used for lookup while parsing
    styles.

    If you pass a dict of variables, those will be interpolated with the styles
    """

    def __init__(self, lookups=None, variables=None):
        self.lookups = lookups
        self.variables = variables

    def parse_text(self, text: str) -> rich.style.Style:
        """convert a string into rich.style.Style object"""
        style = None
        # interpolate variables into the text
        interp = Interpolator(None, self.variables)
        resolved = interp.interpolate_variables(text)
        if self.lookups:
            # we have lookups, so check to see if the resolved value
            # references one of the lookups, if so, use the lookup
            with contextlib.suppress(KeyError):
                style = self.lookups[resolved]
        if not style:
            # no lookup found, so let's parse the style
            style = rich.style.Style.parse(resolved)
        return style

    def parse_dict(self, raw_styles: dict = None) -> dict:
        """parse each style in a dictionary"""
        new_styles = {}
        if raw_styles:
            for key, styledef in raw_styles.items():
                new_styles[key] = self.parse_text(styledef)
        return new_styles
