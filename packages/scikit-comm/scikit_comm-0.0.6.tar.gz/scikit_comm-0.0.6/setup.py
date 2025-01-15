from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension("skcomm.cython_mods.rx_cython", ["skcomm/cython_mods/rx_cython.pyx"])]

# compile Cython modules
try:
    setup(name="scikit-comm",        
        ext_modules=cythonize(extensions, annotate=True, language_level = "3"),
        zip_safe=False,
    )
# fallback to pure python code
except:
    print('='*74)
    print('WARNING: The Cython extension modules could not be compiled, installing pure python modules instead. This may result in slower code execution.')
    setup(name="scikit-comm")
