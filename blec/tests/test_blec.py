from unittest import TestCase
import blec

class TestBlec(TestCase):
    def test_blend(self):
        colors = ['85de8d', 'd225e8:0.75', '2528e8:0.2']
        result = blec.process(colors, False, blec.Srgb())
        self.assertEqual(result, 'b170da')
