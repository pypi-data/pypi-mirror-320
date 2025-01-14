# gogym/__init__.py
from .api import go, save
from .control import initialize_essential_folder


# 在 gogym 被 import 的时候初始化文件夹
initialize_essential_folder()