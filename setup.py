from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name="PyLaser",
    ext_modules=cythonize([
        "main.py",
        "gcode_generator.py",
        "vectorizer.py",
        "laser_controller.py",
        "canvas_widgets.py",
        "dialogs.py",
        "strings.py",
        "themes.py",
        "help_content.py",
    ], 
    compiler_directives={'language_level': "3"}),
    include_dirs=[numpy.get_include()],
)