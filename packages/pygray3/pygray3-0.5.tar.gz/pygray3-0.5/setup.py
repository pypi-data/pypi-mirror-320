import os
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


AUTHOR = "Smawe"
EMAIL = "1281722462@qq.com"


class BuildExtCommand(build_ext):
    def run(self):
        # 调用父类逻辑
        super().run()
        for ext in self.extensions:
            for source in ext.sources:
                if source[-2:] == ".c":
                    path = os.path.abspath(source)
                    print("removing file ->", path)
                    os.remove(path)


extensions = [
    Extension(
        name="pygray3.extensions.key",  # 模块名
        sources=["pygray3/extensions/key.c"],  # Cython 文件
    )
]


setup(
    name='pygray3',
    version='0.5',
    packages=find_packages(where='.', exclude=('tests*',)),
    package_data={"pygray3.extensions": ['*']},
    # ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}, annotate=False),
    ext_modules=extensions,
    cmdclass={'build_ext': BuildExtCommand},
    python_requires='>=3.7',
    install_requires=['pyjwt[crypto]'],
    author=AUTHOR,
    author_email=EMAIL
)
