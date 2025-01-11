import unittest

from .._svgbob import to_svg


class TestSvgbob(unittest.TestCase):

    def test_to_svg(self):
        text = r"""
            /-------\
            | Hello |
            \-------/
        """
        svg = to_svg(text)

    def test_to_svg_unicode(self):
        text = r"""
            ┌───────┐
            │ Hello │
            └───────┘
        """
        svg = to_svg(text)
