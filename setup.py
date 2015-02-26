from distutils.core import setup, Extension
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

ext = Extension("hirlite.hirlite",
    sources=glob.glob("src/*.c"),
    include_dirs=["vendor"])

setup (name='hirlite',
    version=version(),
    description='Python wrapper for hirlite',
    url="https://github.com/seppo0010/hirlite-py",
    author="Pieter Noordhuis",
    author_email="pcnoordhuis@gmail.com",
    keywords=["Rlite"],
    license="BSD",
    packages=["hirlite"],
    ext_modules=[ext],

    # Override "install_lib" command
    cmdclass={ "install_lib": install_lib },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
