from pathlib import Path
import pandas as pd


# setting
HEADLESS = True    # 无头模式（不显示浏览器窗口）
ENABLE_PRINT = True    # 是否启用所有的print语句
ENABLE_LOG = True    # 是否将所有的打印模块重定向到日志中
TIME_WAIT_UNTIL = 60    # wait_until函数的等待时间（单位：秒）
TIME_COOKIE_EXPIRATION = 12    # cookie过期时间（单位：小时）
MAX_LOG_FILES = 5   # logs目录底下最多有几个log文件
MAX_COOKIE_FILES = 3    # cookie目录底下最多有几个cookie文件

# path
PATH_BASE = Path(__file__).resolve().parent    # gogym目录的位置
PATH_COOKIE = PATH_BASE / "data" / "cookies"
PATH_LOG = PATH_BASE / "data" / "logs"
PATH_USER = PATH_BASE / "data" / "users"

# url
URL_IDCALLBACK_INTRANET = "https://ids.xmu.edu.cn/authserver/login?type=userNameLogin&service=http%3A%2F%2Fcgyy.xmu.edu.cn%2Fidcallback"
URL_IDCALLBACK_INTERNET = "https://applg.xmu.edu.cn/wengine-auth/login?id=409&path=/&from=https://cgyy.xmu.edu.cn/room/1"
URL_MY_RESERVATION = "https://cgyy.xmu.edu.cn/my_reservations/slot"
URL_RESERVATION = "https://cgyy.xmu.edu.cn/room/1"

# CONDITION 用于根据页面的提示得到是否该继续预约的flag标志
CONDITIONS = pd.DataFrame(columns=["ret", "key", "value"])
CONDITIONS.loc["fulled"] = [0, "您选择的时段已被约满。", "不顺利：无法预约：您选择的时段已被约满。"]
CONDITIONS.loc["closed"] = [0, "您选择的时间段未开放。", "不顺利：无法预约：您选择的时间段未开放。"]
CONDITIONS.loc["passed"] = [0, "您选择的预定时间段已过。", "不顺利：您选择的预定时间段已过。"]
CONDITIONS.loc["unlogin"] = [0, "后再提交预约。", "不顺利：cookie未成功添加进driver实例。"]
CONDITIONS.loc["booked_for_another_slot"] = [-1, "最多", "不顺利：您一天最多只能预约1个时段。"]
CONDITIONS.loc["booked_for_this_slot"] = [-1, "您已预约该时段。", "不顺利：无法预约：您已预约该时段。"]
CONDITIONS.loc["available"] = [1, "申请场地", "顺利：可以预约：此时间段仍有空余。"]

# slot与具体时间段互相转换的字典
GYM_INDEX_SLOT = {
    1: "10:30-12:00",
    2: "12:00-13:30",
    3: "13:30-15:00",
    4: "15:00-16:30",
    5: "16:30-18:00",
    6: "18:00-19:30",
    7: "19:30-21:00",
}
