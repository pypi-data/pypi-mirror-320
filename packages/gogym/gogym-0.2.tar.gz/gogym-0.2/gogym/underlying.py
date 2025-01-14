# 此文件是底层函数，不会调用本项目的任何包（除了config.py）
# 此文件只包括：日期相关。
from datetime import datetime, timedelta
from gogym.config import TIME_COOKIE_EXPIRATION


def get_date_now(sep="-"):
    """
    这个函数会以2025-01-01的格式返回当前日期
    :param sep: 年月日之间用什么链接，默认为"-"
    :return: 2025-01-01
    """
    return datetime.now().strftime(f"%Y{sep}%m{sep}%d")


def get_date_next_week(sep="-"):
    """
    在抢最新一天的健身房的时候会用到这个函数。
    这个函数会返回最新一天（五天半以后）的日期。
    :param sep: 年月日之间用什么链接，默认为"-"
    :return: 2024-12-14
    """
    # 获取最新一天的日期
    current_datetime = datetime.now()
    future_time = current_datetime + timedelta(days=5, hours=12)
    latest_date = future_time.date()

    # 改变格式
    latest_date_str = latest_date.strftime(f"%Y{sep}%m{sep}%d")

    return latest_date_str


def date_to_weekday(date_str):
    """
    这个函数使用datetime库将2024-12-14这样的输入转化成星期几的输出
    :param date_str: 2024-12-14
    :return: 星期二
    """
    # 获得分割符的格式，防止有时候传入"/"有时候传入"-"
    sep = date_str[4]

    # 从输入得到标准的datetime格式
    date_obj = datetime.strptime(date_str, f"%Y{sep}%m{sep}%d").date()

    # 从datetime格式得到星期几，其中0表示周一，6表示周日
    week_day_num = date_obj.weekday()

    # 定义一个映射表，将0-6映射到中文星期
    week_map = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期天"]
    week_day = week_map[week_day_num]

    return week_day


def is_date_valid(date_str:str, sep="-"):
    """
    这个函数会检查一个date是否是按照一定的格式来的。
    例如 2025-01-01 在char="-" 的情况下是返回True的。
    :param date_str: str
    :param sep: str
    :return: bool value.
    """
    try:
        # 尝试转化为datetime的格式
        datetime.strptime(date_str, f"%Y{sep}%m{sep}%d")
        return True

    except ValueError as e:
        # 如果转不过来就是有问题
        print("不顺利：日期格式不正确或不合法", e)
        return False


def is_cookie_valid(date_str):
    """
    本函数会判断现在的时间是否大于一个给定的时间12小时之内。
    这个函数会用在判定cookie过期没有。
    如果时间超过了十二个小时就返回False，没有超过就返回True。
    :param date_str: '2024_12_20_16_06_06'
    :return: bool value
    """
    # 根据str的时间格式转化成标准格式
    time_format = "%Y_%m_%d_%H_%M_%S"
    given_time = datetime.strptime(date_str, time_format)

    # 获取现在时间
    now_time = datetime.now()

    # 现在的时间做差，看看比给定的时间大多少
    delta_time = now_time - given_time

    # 如果小于12小时，返回True；超过12小时，返回False
    if delta_time >= timedelta(hours=TIME_COOKIE_EXPIRATION):
        return False
    else:
        return True






