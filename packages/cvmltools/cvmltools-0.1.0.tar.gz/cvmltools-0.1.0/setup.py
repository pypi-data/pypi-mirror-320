from setuptools import setup, find_packages
from Cython.Build import cythonize
setup(
    name='cvmltools',  # 包的名称，要符合Python包命名规范，尽量简短且唯一
    version='0.1.0',  # 包的版本号，遵循语义化版本规范，如x.y.z
    # ext_modules=cythonize(
    #     "cluster.cp38-win_amd64.pyd",  # 对 your_package 目录下的所有.pyx 文件进行处理
    #     compiler_directives={
    #         'language_level': 3,  # 确保使用 Python 3 的语法
    #         'always_allow_keywords': False,  # 关闭关键字参数使用
    #         'boundscheck': False,  # 关闭边界检查
    #         'wraparound': False  # 关闭负索引检查
    #     }
    # ),
    zip_safe=False,  # 通常设置为 False，因为 Cython 编译的代码不是 zip 安全的
    description='leo function',  # 对包的简短描述
    author='leo',  # 作者名字
    author_email='your_email@example.com',  # 作者邮箱
    packages=find_packages(),  # 自动查找项目中的所有Python包，会递归查找包含__init__.py的文件夹
    install_requires=[
        # 这里列出项目依赖的其他Python包及其版本要求，例如：
        'numpy>=1.16.0',
        'opencv-python>=4.3.0',
    ],
    classifiers=[
        # 分类器，用于帮助索引你的包，可按实际情况添加，比如：
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)