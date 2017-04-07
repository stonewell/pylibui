from distutils.core import setup, Extension
import distutils
import platform
import os

extra_link_args = []
runtime_library_dirs = []
lib_name_prefix=''
if platform.system() == 'Darwin':
    extra_link_args.append('-Wl,-rpath,' + os.path.join(distutils.sysconfig_get_python_lib(), 'pylibui'))
elif platform.system() == 'Linux':
    runtime_library_dirs.append('$ORIGIN')
elif platform.system() == 'Windows':
    lib_name_prefix='lib'

libui_module = Extension('pylibui._libui',
                             ['pylibui/libui.i'],
                             libraries=[lib_name_prefix+'ui'],
                             runtime_library_dirs=runtime_library_dirs,
                             extra_link_args = extra_link_args
                             )


setup(
    name='pylibui',
    version='0.0.1',
    ext_modules=[libui_module],
    description='Python wrapper for libui',
    packages=['pylibui', 'pylibui.controls']
)
