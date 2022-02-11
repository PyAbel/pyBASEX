# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division

import numpy as np
from numpy.testing import assert_allclose, assert_equal

# to suppress deprecation warnings
from warnings import catch_warnings, simplefilter

from abel.tools.analytical import SampleImage
from abel import Transform


def test_sample_Dribinski():
    """
    Test SampleImage 'Dribinski'.
    """
    # test deprecated attribute
    test = SampleImage(name='dribinski')  # (test lower-case)
    with catch_warnings():
        simplefilter('ignore', category=DeprecationWarning)
        assert_equal(test.image, test.func)

    # .abel is difficult to test reliably due to the huge dynamic range

    # test scaling
    n = 501
    test1 = SampleImage(n=n, name='Dribinski', sigma=2)
    test2 = SampleImage(n=n // 2 + 1, name='Dribinski', sigma=1)  # halved
    assert(test2.r_max == test1.r_max / 2)
    assert_allclose(test2.func, test1.func[::2, ::2])
    assert_allclose(test2.abel, test1.abel[::2, ::2] / 2, atol=2e-6)


def test_sample_Ominus():
    """
    Test SampleImage 'Ominus'.
    """
    # SampleImage options, recon tolerance
    param = [(dict(), 0.2),
             (dict(n=501), 0.073),
             (dict(sigma=3), 0.056),
             (dict(n=501, sigma=3), 0.14),
             (dict(temperature=100), 0.2)]

    for kwargs, tol in param:
        test = SampleImage(name='Ominus', **kwargs)
        # test deprecated .image attribute
        with catch_warnings():
            simplefilter('ignore', category=DeprecationWarning)
            assert_equal(test.image, test.func)

        # test transform (Daun with cubic splines is the most accurate)
        recon = Transform(test.abel, method='daun', symmetry_axis=(0, 1),
                          transform_options={'degree': 3,
                                             'verbose': False}).transform
        assert_allclose(recon, test.func, atol=tol,
                        err_msg='-> abel, {}'.format(kwargs))

    # test transform tol
    test = SampleImage(name='Ominus')
    abel = test.abel.copy()  # default, ≲5e-3
    abel4 = test.transform(1e-4)
    abel5 = test.transform(1e-5)
    ampl = np.max(abel5)
    assert_allclose(abel, abel5, atol=3e-3 * ampl)
    assert_allclose(abel4, abel5, atol=0.3e-4 * ampl)


if __name__ == "__main__":
    test_sample_Dribinski()
    test_sample_Ominus()
