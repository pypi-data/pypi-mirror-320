# api.py文件可以调用本项目的任何包
# 用户也只允许调用api.py的包
from multiprocessing import Process

from gogym.control import (initialize_essential_folder,
                           get_safe_shared_list,
                           rewrite_print,
                           is_user_exist,
                           generate_log)
from gogym.driver import (get_available_slot_list,
                          go_user,
                          get_reservation_info, User)
from gogym.underlying import get_date_next_week


def go(date=get_date_next_week()) -> bool:
    """
    此函数会用多进程让每个账号都预约下周的健身房。
    注：在爬当天的预约信息时会匿名访问一次服务器。
    :return: True
    """
    # 检查是否有必要文件夹，没有则新建
    initialize_essential_folder()

    # 日志记录：生成一个安全列表，并重写print
    backup = get_safe_shared_list()
    rewrite_print(backup)

    # 如果 users 目录里没有用户的 json 则提示需要保存并推出
    if not is_user_exist():
        print(f"data/users目录中没有用户，请调用User.save()函数保存新用户。")
        generate_log(backup)
        return False

    # 打印下周当天的预信息
    print(f"-----------------------------------当天预约信息-----------------------------------")
    available_slot_list = get_available_slot_list(date, show=True)

    # 如果列表为空，表示当天已经没有可以预约的时间段
    if not available_slot_list:
        print(f"------------------------{date} 当天已经没有时间段可以预约-----------------------")
        generate_log(backup)
        return False

    # 将每个用户的go_user进程都添加到进城池pool里
    pool = []
    for user in User.get_info()[:, 0]:
        each = Process(target=go_user, args=(user, date, available_slot_list, backup), name=f"Process-{user}")
        pool.append(each)

    # 启动所有进程
    for each in pool:
        each.start()
    print(f"----------------------------------所有进程已启动----------------------------------")

    # 等待所有进程结束
    for each in pool:
        each.join()
    print(f"----------------------------------所有进程已完成----------------------------------")

    # 打印所有用户今天所抢的健身房
    get_reservation_info(user="all", date=date, is_print=True)

    # 日志记录：生成日志文件
    generate_log(backup)
    return True

