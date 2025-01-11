import os
from setuptools import setup, find_packages
from Cython.Distutils import Extension
from setuptools.command.build_ext import build_ext


class BuildExtCommand(build_ext):
    def run(self):
        # 调用父类逻辑
        super().run()
        # 删除 `.c` 文件
        for ext in self.extensions:
            for source in ext.sources:
                print("removing file ->", os.path.abspath(source))
                os.remove(os.path.abspath(source))


extensions = [
    Extension(
        name="pygray3.extensions.key",  # 模块名
        sources=["pygray3/extensions/key.c"],  # Cython 文件
    )
]


setup(
    name='pygray3',
    version='0.1',
    packages=find_packages(where='.', exclude=('tests',)),
    include_package_data=True,
    # ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}, annotate=False),
    ext_modules=extensions,
    cmdclass={'build_ext': BuildExtCommand},
    python_requires='>=3.7',
    install_requires=['pyjwt'],
)
