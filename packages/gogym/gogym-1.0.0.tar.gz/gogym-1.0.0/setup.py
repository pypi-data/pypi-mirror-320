from setuptools import setup, find_packages


setup(
    name="gogym",
    version="1.0.0",
    description="One click is all you need",
    author="taolar",
    author_email="hujinlong@stu.xmu.edu.cn",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.24.0",
        "numpy>=2.0.1",
        "pandas>=2.2.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

"""
使用方式：

# 清理上次产生的缓存
rm -rf dist/ build/ GoGym.egg-info

# 打包
python -m build

# 从环境中卸载包
pip uninstall GoGym

# 从本地安装包
pip install dist/GoGym-0.2-py3-none-any.whl

# 打开python
python

# 引用并且输出
from GoGym import go
go()


--------------------------------------------------------------------------
GoGym
rm -rf dist/ build/ GoGym.egg-info
python -m build
twine upload dist/*
--------------------------------------------------------------------------
6
pip uninstall GoGym
pip install /Users/hujinlong/PycharmProjects/GoGym/dist/GoGym-0.2-py3-none-any.whl
--------------------------------------------------------------------------




pip uninstall GoGym
pip install dist/GoGym-0.2-py3-none-any.whl


"""
