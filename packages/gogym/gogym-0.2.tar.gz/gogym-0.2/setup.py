from setuptools import setup, find_packages


def parse_requirements(filename="requirements.txt"):
    """
    这个函数会读取 requirements.txt 里的依赖并返回。
    :param filename:
    :return:
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().splitlines()

setup(
    name="GoGym",
    version="0.2",
    description="One click is all you need",
    packages=find_packages(),  # 自动去找所有含 __init__.py 的目录
    python_requires='>=3.8',
    include_package_data=True,  # 需要这行来启用 MANIFEST.in 规则
    install_requires=[
        "selenium>=4.24.0",
        "numpy>=2.0.1",
        "pandas>=2.2.3",
    ],
    # 其他元数据...
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
--------------------------------------------------------------------------
6
pip uninstall GoGym
pip install /Users/hujinlong/PycharmProjects/GoGym/dist/GoGym-0.2-py3-none-any.whl
--------------------------------------------------------------------------




pip uninstall GoGym
pip install dist/GoGym-0.2-py3-none-any.whl


"""
