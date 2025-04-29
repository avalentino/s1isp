"""Setup script for s1isp."""

import numpy as np
import setuptools

extensions = [
    setuptools.Extension(
        "s1isp._huffman",
        sources=["s1isp/_huffman.pyx", "src/huffman.c"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        include_dirs=["src", np.get_include()],
    )
]
setuptools.setup(ext_modules=extensions)
