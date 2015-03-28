from setuptools import setup, Extension
from distutils.command import install_lib as _install_lib
import imp, glob

def version():
    module = imp.load_source("hirlite.version", "hirlite/version.py")
    return module.__version__

# Patch "install_lib" command to run build_clib before build_ext
# to properly work with easy_install.
# See: http://bugs.python.org/issue5243
class install_lib(_install_lib.install_lib):
    def build(self):
        if not self.skip_build:
            if self.distribution.has_pure_modules():
                self.run_command('build_py')
            if self.distribution.has_c_libraries():
                self.run_command('build_clib')
            if self.distribution.has_ext_modules():
                self.run_command('build_ext')

# To link the extension with the C library, distutils passes the "-lLIBRARY"
# option to the linker. This makes it go through its library search path. If it
# finds a shared object of the specified library in one of the system-wide
# library paths, it will dynamically link it.
#
# We want the linker to statically link the version of hirlite that is included
# with hirlite-py. However, the linker may pick up the shared library version
# of hirlite, if it is available through one of the system-wide library paths.
# To prevent this from happening, we use an obfuscated library name such that
# the only version the linker will be able to find is the right version.
#
# This is a terrible hack, but patching distutils to do the right thing for all
# supported Python versions is worse...
#
# Also see: https://github.com/pietern/hiredis-py/issues/15
lib = ("hirlite_for_hirlite_py", {
  "include_dirs": [
  'vendor/rlite/src',
  'vendor/rlite/deps/lua/src'
  ],
  "sources": (
      [f for f in glob.glob("vendor/rlite/src/*.c") if '_win' not in f] +
      glob.glob("vendor/rlite/deps/*.c") +
      glob.glob("vendor/rlite/deps/lua/src/*.c")
      )})

ext = Extension("hirlite.hirlite",
    sources=glob.glob("src/*.c"),
    include_dirs=["vendor/rlite/src"])

setup (name='hirlite',
    version=version(),
    description='Python wrapper for rlite',
    url="https://github.com/seppo0010/rlite-py",
    author="Sebastian Waisbrot",
    author_email="seppo0010@gmail.com",
    keywords=["Redis", "rlite"],
    license="BSD",
    packages=["hirlite"],
    libraries=[lib],
    ext_modules=[ext],

    # Override "install_lib" command
    cmdclass={ "install_lib": install_lib },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
    ],
)
