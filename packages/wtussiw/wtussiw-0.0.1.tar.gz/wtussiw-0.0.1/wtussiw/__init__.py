import calendar
import datetime
import os
import subprocess
import time
import pyautogui as pa
import pyperclip
import win32com.client as win32


def get_first_and_last_day():
    """返回包含当天、本月第一天和本月最后一天的日期列表"""
    try:
        today = datetime.date.today()
        year = today.year
        month = today.month
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(year, month)[1])
        return [today, first_day, last_day]
    except Exception as e:
        print(f"Error occurred: {e}")
        return []


def get_file_modified_date(file_path):
    """获取文件的最后修改时间。文件不存在返回None"""
    try:
        timestamp = os.stat(file_path)
        modified_time = datetime.datetime.fromtimestamp(timestamp.st_mtime)
        return modified_time
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error accessing file {file_path}: {e}")
        return None


def get_equality(f1, f2):
    """判断文件1和文件2的最后修改时间是否和当小时数相同"""
    if not os.path.exists(f1) or not os.path.exists(f2):
        return 'file not exists'
    erp = get_file_modified_date(f1).strftime('%Y%m%d%H')
    hd = get_file_modified_date(f2).strftime('%Y%m%d%H')
    th = datetime.datetime.now().strftime('%Y%m%d%H')
    if erp == th and hd == th:
        return 'equality'
    else:
        return 'not equality'


def locate_pic(path, match=0.85, times=77):
    if not os.path.isfile(path):
        return f'File does not exist or is not a file: {path}'
    for cnt in range(times):
        try:
            time.sleep(1)
            return pa.locateOnScreen(path, confidence=match)
        except pa.ImageNotFoundException:
            print(f"Retrying after 1 second... {times - cnt} times left")
            continue
    return 'not found'


def click_pic(img_path, match=0.85, times=77, left=0, top=0):
    """
    默认点击图片中心位置，否则点击参数指定位置
    img_path: 图片路径、match: 匹配度、times: 重试次数、left: 右偏移量、top: 下偏移量
    """
    try:
        loc = locate_pic(img_path, match, times)
        if left != 0 and top != 0:
            pa.click(loc.left + left, loc.top + top)
        else:
            pa.click(loc.left + loc.width // 2, loc.top + loc.height // 2)
    except Exception as e:
        print(f"Error occurred: {e}")


def wx_search_user(username, img_path):
    """搜索用户,并点击搜索到的用户，以便切换到用户界面
    img_path: 图片文件目录、username: 微信用户名"""
    for i in ['C:\\Program Files', 'D:\\Program Files', 'C:\\Program Files (x86)']:
        try:
            subprocess.Popen(fr'{i}\Tencent\WeChat\WeChat.exe')
            break
        except WindowsError:
            print(f'程序不在{i}\\Tencent\\WeChat\\WeChat.exe中')
    loc_user = locate_pic(fr'{img_path}\user.png')
    pa.click(loc_user.left + 77, loc_user.top + 12)
    pyperclip.copy(username)
    time.sleep(1)
    pa.hotkey('ctrl', 'v')
    time.sleep(1.5)
    pa.click(loc_user.left + 77, loc_user.top + 98)


def send_msg_text(ps):
    """param ps: {'user': '微信用户名', 'msg': '要发送的文本内容','img_path':'图片所在目录'}"""
    wx_search_user(ps['user'], fr'{ps["img_path"]}')  # 搜索用户并切换到用户界面
    # 点击文本输入框，并输入需要发送的文本内容和点击发送按钮
    click_pic(fr'{ps["img_path"]}\msg.png',left=100,top=77)
    pyperclip.copy(ps['msg'])
    pa.hotkey('ctrl', 'v')
    time.sleep(2)
    pa.press('enter')
    # 点击【关闭】按钮
    click_pic(fr'{ps["img_path"]}\close.png',left=12,top=12)


def send_msg_file(ps):
    """param ps: {'user': '微信用户名', 'filename': r'待发送文件完整路径','img_path':'图片所在目录'}"""
    wx_search_user(ps['user'], fr'{ps["img_path"]}')  # 搜索用户并切换到用户界面
    click_pic(fr'{ps["img_path"]}\filebtn.png')     # 点击发送文件【图片按钮】
    time.sleep(2)
    pyperclip.copy(ps['filename'])
    pa.hotkey('ctrl', 'v')
    time.sleep(2)
    pa.press('enter')
    click_pic(fr'{ps["img_path"]}\sendbtn.png')   # 点击【发送】按钮
    click_pic(fr'{ps["img_path"]}\close.png')       # 点击【关闭】按钮


def wait_for_appear(img_path, times=30, match=0.85):  # 等待元素出现，默认等待30秒
    for i in range(times):
        time.sleep(1)
        try:
            pa.locateOnScreen(fr'{img_path}', confidence=match)
            break
        except Exception as e:
            print(f"已经等待了{i + 1}秒，元素未出现，继续等待...{e}")
            continue


def wait_for_disappear(img_path, times=30, match=0.85):  # 等待元素消失，默认等待30秒
    for i in range(times):
        time.sleep(1)
        try:
            pa.locateOnScreen(img_path, confidence=match)
            print(f'waiting for {i + 1}s')
            continue
        except Exception as e:
            print(str(e))
            break


def wait_appear_or_disappear(option, img_path, times=20, match=0.8):
    """
    :param option: 0表示等待元素出现，1表示等待元素消失
    :param img_path: 图片完整路径
    :param times: 重试次数，每次等1秒,默认20次
    :param match: 匹配度
    """
    if option == 0:
        wait_for_appear(img_path, times, match)
    elif option == 1:
        wait_for_disappear(img_path, times, match)
    else:
        raise Exception('option参数错误')


def execute_macro(args):
    """
    param:{'file_path': r'带宏excel文件路径', 'sheet_name': '工作表名', 'macro_name': '宏名称'}
    """
    # 参数验证
    required_keys = ['file_path', 'sheet_name', 'macro_name']
    if not all(key in args for key in required_keys):
        raise ValueError("缺少必需的参数: {}".format(", ".join(required_keys)))
    excel = win32.gencache.EnsureDispatch("Excel.Application")  # 创建Excel应用程序对象
    excel.Visible = True  # 设置可见，默认不可见False
    # 打开已存在的Excel文件
    try:
        workbook = excel.Workbooks.Open(args['file_path'], UpdateLinks=True)  # 更新链接
        worksheet = workbook.Worksheets(args['sheet_name'])  # 获取工作表对象
        worksheet.Activate()
        excel.Run(args['macro_name'])  # 调用VBA函数
        workbook.Close(SaveChanges=True)  # 关闭并保存Excel文件
    except Exception as e:
        print("执行宏时出错：", str(e))
    finally:
        if excel is not None:
            excel.Quit()  # 退出Excel应用程序


if __name__ == '__main__':
    pass