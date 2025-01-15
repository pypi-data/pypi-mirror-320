from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
from distutils.errors import CompileError

class GetPybindInclude:
    def __init__(self, user: bool = False):
        self.user = user

    def __str__(self) -> str:
        import pybind11
        return pybind11.get_include(self.user)

ext_modules = [
    Extension(
        "simple_ans._simple_ans",
        ["simple_ans_bind.cpp", "simple_ans/cpp/simple_ans.cpp"],
        include_dirs=[
            str(GetPybindInclude()),
            str(GetPybindInclude(user=True)),
            "simple_ans/cpp",
            "."  # Add root directory to include path
        ],
        language='c++'
    ),
]

def has_flag(compiler, flagname: str) -> bool:
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False) as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except CompileError:
        return False
    finally:
        try:
            import os
            os.remove(fname)
        except OSError:
            pass
    return True

def cpp_flag(compiler) -> str:
    flags = ['-std=c++17', '-std=c++14', '-std=c++11']
    for flag in flags:
        if has_flag(compiler, flag):
            return flag
    raise RuntimeError('Unsupported compiler -- at least C++11 support is needed!')

class BuildExt(build_ext):
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.7']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')

        for ext in self.extensions:
            ext.define_macros = [('VERSION_INFO', '"{}"'.format(self.distribution.get_version()))]
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)

setup(
    name='simple_ans',
    version='0.1.0',
    author='Jeremy Magland',
    author_email='jmagland@flatironinstitute.org',
    description='Simple ANS (Asymmetric Numeral Systems) implementation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/magland/simple_ans',
    packages=['simple_ans'],
    install_requires=[
        'numpy>=1.19.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.7',
    ext_modules=ext_modules,
    setup_requires=['pybind11>=2.5.0'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
