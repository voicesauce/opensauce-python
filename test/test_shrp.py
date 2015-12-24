import numpy as np

from opensauce.shrp import window

from test.support import TestCase, parameterize

@parameterize
class TestSHRP(TestCase):

    window_params = dict(
        rect10=('rect', 10, None, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
        rect3=('rectangular', 3, None, [1, 1, 1]),
        rect4=('rectan', 4, None, [1, 1, 1, 1]),
        tria10=('tria', 10, None,
            [0.00000, 0.22222, 0.44444, 0.66667, 0.88889,
             0.88889, 0.66667, 0.44444, 0.22222, 0.00000]),
        tria3=('triangular', 3, None, [0, 1, 0]),
        hann10=('hann', 10, None,
            [0.00000, 0.11698, 0.41318, 0.75000, 0.96985,
             0.96985, 0.75000, 0.41318, 0.11698, 0.00000]),
        hann3=('hanning', 3, None, [0, 1, 0]),
        hamm10=('hamm', 10, None,
            [0.080000, 0.187620, 0.460122, 0.770000, 0.972259,
             0.972259, 0.770000, 0.460122, 0.187620, 0.080000]),
        hamm3=('hamming', 3, None, [0.080000, 1.00000, 0.080000]),
        blac10=('blac', 10, None,
            [-1.3878e-17, 5.0870e-02, 2.5800e-01, 6.3000e-01, 9.5113e-01,
              9.5113e-01, 6.3000e-01, 2.5800e-01, 5.0870e-02, -1.3878e-17]),
        black3=('blackman', 3, None, [-1.3878e-17, 1.0000e+00, -1.3878e-17]),
        # XXX: I don't know what beta is, and don't need to find the answer for
        # this project.
        #kais10=('kais', 10, ?, []),
        #kais10_2=('kaiser', 10, ?, []),
        #kais3=('kais', 3, ?, []),
        #kais3_2=('kais', 3, ?, []),
        )

    def window_as_window_args(self, window_type, window_width, beta, expected):
        res = window(window_width, window_type, beta)
        self.assertIsInstance(res, np.ndarray)
        # octave gives results to five places (single precision float?)
        for i in range(len(expected)):
            self.assertAlmostEqual(res[i], expected[i], places=5,
                                   msg='at index {}:\n{}\n  vs\n{}'.format(
                                        i, res, expected))

    def test_window_bad_window_type(self):
        with self.assertRaises(ValueError):
            window(10, 'bad')
        with self.assertRaises(ValueError):
            window(10, 'longerbad')
        with self.assertRaises(ValueError):
            window(10, 'rec')   # Not four chars.

    def test_kais_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            window(10, 'kais', 0)
