import random
import time
from enum import Enum

import DrissionPage
from DrissionPage._pages.mix_tab import MixTab

class SleepTime(Enum):
    MOUSE_RELEASE = (0.1, 0.2)
    HUMAN_THINK = (0.2, 3)
    WAIT_PAGE = (1, 1.5)

def sleep(sleep_time: SleepTime):
    time.sleep(random.uniform(sleep_time.value[0], sleep_time.value[1]))

def move_to(tab: MixTab, ele_or_loc):
    act = tab.actions
    return act.move_to(ele_or_loc, random.randint(5, 7), random.randint(5, 7), random.uniform(0.5, 1.0))

def click(tab: MixTab, ele_or_loc, more_real=True):
    act = tab.actions
    sleep(SleepTime.HUMAN_THINK)
    if more_real:
        move_to(tab, ele_or_loc).hold()
        sleep(SleepTime.MOUSE_RELEASE)
        act.release()
    else:
        move_to(tab, ele_or_loc)
        tab.ele(ele_or_loc).click()
        
    sleep(SleepTime.WAIT_PAGE)

def type(tab: MixTab, ele_or_loc, message: str, more_real=True):
    act = tab.actions
    sleep(SleepTime.HUMAN_THINK)
    # 没有指定元素，则直接模拟键盘输入
    if not ele_or_loc:
        act.type(message)
    else:
        if more_real:
            click(tab, ele_or_loc)
            act.type(message)
        else:
            tab.ele(ele_or_loc).input(message)
        
    sleep(SleepTime.WAIT_PAGE)

def scroll(tab: MixTab, ele_or_loc, delta_y, delta_x):
    act = tab.actions
    move_to(tab,ele_or_loc)
    act.scroll(delta_y, delta_x)
