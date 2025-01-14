from setuptools import setup, find_packages


setup(
    name="gogym",
    version="1.0.1",
    description="One click is all you need",
    author="taolar",
    author_email="hujinlong@stu.xmu.edu.cn",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.24.0",
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
--------------------------------------------------------------------------
----------------------------------老环境----------------------------------
打包
上传 github
rm -rf dist/ build/ gogym.egg-info
python -m build

新环境本地测试
conda activate test
pip uninstall gogym
pip install /Users/hujinlong/PycharmProjects/GoGym/dist/gogym-1.0.1-py3-none-any.whl
pip show gogym

python
from gogym import *
看看有没有文件夹
go()
save(initial="hjl", name="", account="36920241153211", password="Hjl2001032", phone="13871112939", slot_preference=[4, 5, 6, 7])
save(initial="hjl", name="", account="36920241153211", password="Hjl20010320", phone="13871112939", slot_preference=[4, 5, 6, 7])
go()
--------------------------------------------------------------------------
----------------------------------新环境-----------------------------------
打包
上传 github
rm -rf dist/ build/ gogym.egg-info
python -m build

新环境本地测试
conda create -n test1
conda activate test1
conda install pip
pip install /Users/hujinlong/PycharmProjects/GoGym/dist/gogym-1.0.1-py3-none-any.whl
pip show gogym

python
from gogym import *
要看一下有没有文件夹创建出来
save(initial="hjl", name="", account="36920241153211", password="Hjl2001032", phone="13871112939", slot_preference=[4, 5, 6, 7])
save(initial="hjl", name="", account="36920241153211", password="Hjl20010320", phone="13871112939", slot_preference=[4, 5, 6, 7])
go()
--------------------------------------------------------------------------
----------------------------------联网新环境-----------------------------------
打包
上传 github
rm -rf dist/ build/ gogym.egg-info
python -m build

新环境本地测试
conda create -n test1
conda activate test1
conda install pip
pip install /Users/hujinlong/PycharmProjects/GoGym/dist/gogym-1.0.1-py3-none-any.whl
pip show gogym

python
from gogym import *
要看一下有没有文件夹创建出来
save(initial="hjl", name="", account="36920241153211", password="Hjl2001032", phone="13871112939", slot_preference=[4, 5, 6, 7])
save(initial="hjl", name="", account="36920241153211", password="Hjl20010320", phone="13871112939", slot_preference=[4, 5, 6, 7])
go()
--------------------------------------------------------------------------













联网测试
pip uninstall gogym
pip install gogym 
--------------------------------------------------------------------------
twine upload dist/*

"""
