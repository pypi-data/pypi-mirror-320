# 此文件有关：定制化输出、日志、文件管理。
import builtins
import multiprocessing
import os
import shutil
from datetime import datetime
from gogym.config import *


def customized_print(shared_list):
    # 记录 python 的原生 print 函数
    original_print = builtins.print

    def p(*args, **kwargs):
        """
        打印内容
        保存内容
        :return:
        """
        # 获取当前时间戳，格式为 "YYYY-MM-DD HH:MM:SS:ms"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]  # 取前3位微秒作为毫秒

        # 拼接要打印的消息
        message = " ".join(str(a) for a in args)

        # 将带有时间戳的消息保存到共享列表
        shared_list.append(f"{timestamp} {message}")

        # 如果启用打印则打印到控制台
        if ENABLE_PRINT:
            original_print(*args, **kwargs)

    return p


def get_safe_shared_list():
    """
    得到一个不用担心写冲突的共享列表。
    :return:
    """
    manager = multiprocessing.Manager()
    lis = manager.list()
    return lis


def rewrite_print(backup):
    """
    在父进程或者子进程中使用这个函数来改写原生 print 函数。
    :param backup: 安全列表
    :return:
    """
    builtins.print = customized_print(backup)


def generate_log(backup):
    """
    此函数会把所有打印的输出（存在buckup中）保存为一个 log 文件
    其实我这样做还有一个好处，就是调试的时候是可以不新增日志的。
    :param backup:
    :return:
    """
    # 如果不启用日志记录，直接退出
    if not ENABLE_LOG:
        return False

    # 生成带有当前日期和时间的日志文件名
    current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    log_filepath = PATH_LOG / f'log_{current_time}.log'

    # 将内容写到 log 文件中
    with open(log_filepath, "w", encoding="utf-8") as f:
        for line in backup:
            f.write(line + "\n")

    # 管理日志文件
    manage_log_file()

    return True


def manage_file(path, max_files, file_suffix):
    """
    这个函数传入一个目标文件夹，以及目标文件夹里放的文件的数量，
    这个函数会讲more子文件夹里的数量按照max_files多退少补。
    :param file_suffix: 文件格式以什么结尾。eg:".log", ".json"
    :param path: Path instance
    :param max_files: int
    :return: bool value
    """
    # 对 max_files 进行越界判断
    if max_files < 0:
        raise ValueError("max_files小于0，输入不合法。")

    # 确认 path 目录和 path/more 子目录都在，如果不存在则创建一个
    path_more = Path(path) / "more"
    path_more.mkdir(parents=True, exist_ok=True)

    # 列出 path 文件夹下所有文件，找出谁比谁多
    files = [f for f in os.listdir(path) if f.endswith(file_suffix)]
    delta = len(files) - max_files

    # 如果文件数量超过了 max_files 则把超过的部分移到path_more里
    if delta > 0:

        # 按照文件名中的时间戳排序，得到需要被放到more文件夹里的若干个文件的文件名
        files_sorted = sorted(files, key=lambda x: datetime.strptime(x[:-len(file_suffix)][-19:], '%Y_%m_%d_%H_%M_%S'))
        files_to_move = files_sorted[:delta]

        # 对每个需要被移动到more文件夹里的文件都移动到more文件夹中
        for each_file in files_to_move:
            path_scr = path / each_file
            path_dst = path_more / each_file
            # 移动文件
            try:
                shutil.move(path_scr, path_dst)
            except Exception as e:
                print(f"移动文件 {each_file} 失败: {e}")
                return False
        return True

    # 如果 path 里的文件少于 max_files 则在 path/more 文件夹里找出差的部分，移动到 path 里面
    elif delta < 0:

        # 在 path/more 文件夹里找出文件，排序，得到最新的 delta 个文件
        more_files = [f for f in os.listdir(path_more) if f.endswith(file_suffix)]
        # 如果 more 文件夹里有文件，则操作。如果没有文件，就不操作
        if more_files:
            more_files_sorted = sorted(more_files, key=lambda x: datetime.strptime(x[:-len(file_suffix)][-19:], '%Y_%m_%d_%H_%M_%S'), reverse=True)
            more_files_to_move = more_files_sorted[:abs(delta)]

            # 从more文件夹中移动每个待移动文件夹到logs中
            for each_file in more_files_to_move:
                path_scr = path_more / each_file
                path_dst = path / each_file
                # 移动文件
                try:
                    shutil.move(path_scr, path_dst)
                except Exception as e:
                    print(f"移动文件 {each_file} 失败: {e}")
                    return False
            return True
        else:
            # path/more 文件夹里也是空的，没东西移动
            return True
    else:
        # 文件数等于 max file，不需要移动
        return True


def manage_log_file():
    return manage_file(path=PATH_LOG, max_files=MAX_LOG_FILES, file_suffix=".log")


def manage_cookie_file(user):
    return manage_file(path=PATH_COOKIE / user, max_files=MAX_COOKIE_FILES, file_suffix=".json")


def initialize_essential_folder():
    """
    这个函数会初始化必要的文件夹data, cookies, logs, users
    :return:
    """
    # 所有需要初始化的文件夹
    path_list = [PATH_COOKIE, PATH_LOG, PATH_USER]

    # 对每个文件夹，如果不存在则创建
    for each_path in path_list:
        if not each_path.exists():
            each_path.mkdir(parents=True, exist_ok=True)

    return True


def is_user_exist(path_user:Path=PATH_USER) -> bool:
    """
    这个函数会判断 PATH_USER 文件夹下是否有用户的 json 文件。
    如果有文件则返回 True，没有则返回 False。
    :return: bool
    """
    # 如果文件夹没有创建则创建文件夹
    if not path_user.is_dir():
        raise ValueError(f"{path_user} 不是一个有效的目录")

    # 查找 .json 文件
    json_files = list(path_user.glob("*.json"))

    # 返回 1 表示存在，0 表示不存在
    return True if json_files else False