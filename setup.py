from distutils.core import setup
import py2exe

setup(windows=['main.py'],
      options={
          "py2exe": {
              "includes": ["ctypes", "logging"],
              "excludes": ["OpenGL", "setuptools", "numpy", "logging.handlers", "multiprocessing"],
              }
          }
      )