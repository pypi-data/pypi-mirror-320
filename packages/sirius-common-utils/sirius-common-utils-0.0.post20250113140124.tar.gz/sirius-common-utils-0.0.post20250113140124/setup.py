from datetime import datetime

def generate_version():
    now = datetime.now()
    version = now.strftime("%Y%m%d%H%M%S")
    return version

import shutil
shutil.rmtree("dist")

from setuptools import setup, find_packages

setup(
    name="sirius-common-utils",  # 包名
    version="0.0-"+generate_version(),  # 版本号
    author="Joey Yang",  # 作者名
    author_email="156838991@qq.com",  # 作者邮箱
    description="sirius-common-utils",  # 简短描述
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",  # 项目主页
    package_dir={"": "src"},  # 指定源代码目录
    packages=find_packages(where="src"),  # 自动发现包
    classifiers=[  # 分类信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 依赖的 Python 版本
    install_requires=[  # 依赖项
        "requests",
        "numpy"
    ],
)
