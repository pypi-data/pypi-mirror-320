from setuptools import setup, find_packages
from pathlib import Path

# 获取当前目录
current_dir = Path(__file__).parent

setup(
    name="graphworkc",  # 包名称
    version="1.0.7",  # 版本号
    description="A Python wrapper for Graphworkc extension.",  # 描述
    author="ZC",  # 作者
    author_email="1263703239@qq.com",  # 邮箱
    packages=find_packages(),  # 自动查找所有含有 __init__.py 的包
    py_modules=["__init__"],  # 根目录模块
    include_package_data=True,
    package_data={
        "graphworkc": ["graphworkc.cp311-win_amd64.pyd"],  # 包含 .pyd 文件
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.11",
)