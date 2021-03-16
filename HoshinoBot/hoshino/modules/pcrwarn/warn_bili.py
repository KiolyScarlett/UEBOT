import os
import pytz
import random
from datetime import datetime

import nonebot
from hoshino.service import Service, priv
from hoshino import R

svbl = Service('pcrwarn_bili', enable_on_default=False, manage_priv=priv.ADMIN, visible=True)

@svbl.scheduled_job('cron', hour='6')
async def day1_reminder():
    msgs = [
        f'游戏商店内可以买经验药水了哦！\n快和我一起速速升级成为本群最强的骑士君吧！\n(1/4){R.img("栞栞买药2.png").cqcode}\n', 
    #    f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'day1_reminder')

@svbl.scheduled_job('cron', hour='12')
async def day2_reminder():
    #path = 'C:/Resources/MEGUMIN/（小哼）.mp3'
    msgs = [
        f'游戏商店内可以买经验药水了哦！\n快和我一起速速升级成为本群最强的骑士君吧！\n(2/4){R.img("栞栞买药.jpg").cqcode}\n',
    #    f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'day2_reminder')

@svbl.scheduled_job('cron', hour='18')
async def day3_reminder():
    #path = 'C:/Resources/MEGUMIN/（小哼）.mp3'
    msgs = [
        f'游戏商店内可以买经验药水了哦！\n快和我一起速速升级成为本群最强的骑士君吧！\n(3/4){R.img("栞栞买药2.png").cqcode}\n',
    #    f'[CQ:record,file=file:///{F:/Resources/pcrwarn/要感谢我哦.mp3}]'
    ]
    await svbl.broadcast(msgs, 'day3_reminder')
    
@svbl.scheduled_job('cron', hour='23', minute='59')
async def day4_reminder():
    #path = 'C:/Resources/MEGUMIN/（小哼）.mp3'
    msgs = [
        f'游戏商店内可以买经验药水了哦！\n快和我一起速速升级成为本群最强的骑士君吧！\n(4/4){R.img("栞栞买药.jpg").cqcode}\n',
    #    f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'day4_reminder')  
'''
@svbl.scheduled_job('cron', hour='14', minute='40')
async def beici():
    #path = 'C:/Resources/MEGUMIN/有什么好的委托吗.mp3'
    msgs = [
        f'现在是北京时间14点40，距离竞技场结算还有20分钟哦！请注意！{R.img("惠惠竞技场.jpg").cqcode}\n',
    #    f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'beici')
''' 
@svbl.scheduled_job('cron', hour='5')
async def wakeup():
    #path = 'C:/Resources/MEGUMIN/早，早安.mp3'
    msgs = [
        f'早…早安\n',
        f'你醒了么……今天也要元气满满的开始冒险哦！{R.img("IMG111920200613141719.JPG").cqcode}\n',
    #    f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'wakeup') 

'''
@svbl.scheduled_job('cron', hour='12')
async def tili1():
    path = 'C:/Resources/MEGUMIN/话说，我肚子饿了呢.mp3'
    msgs = [
        f'中午的游戏体力可以领取了哦！{R.img("惠惠中午.jpg").cqcode}\n',
        f'话说，我肚子饿了呢\n',
        f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'tili1')     
    
@svbl.scheduled_job('cron', hour='18')
async def tili2():
    path = 'C:/Resources/MEGUMIN/欢迎回来.mp3'
    msgs = [
        f'欢迎回来！\n',
        f'下午的游戏体力可以领取了哦！{R.img("惠惠下午.jpg").cqcode}\n',
        f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'tili2') 
    
@svbl.scheduled_job('cron', hour='0', minute='30')
async def sleep():
    path = 'C:/Resources/MEGUMIN/没办法了呢，久违地陪你吧.mp3'
    msgs = [
        f'已经12点半了哦~你也要早点休息！{R.img("惠惠晚安.jpg").cqcode}\n',
        f'没办法了呢，久违地陪你吧\n'
        f'[CQ:record,file=file:///{path}]'
    ]
    await svbl.broadcast(msgs, 'sleep') 
'''