
import os
import re
from nonebot import on_command
from hoshino import util, R
from hoshino.service import Service, priv
sv = Service('log', manage_priv=priv.SUPERUSER, visible=False, enable_on_default=True)
# 新增：
LOG = '''
2021.03.15 优衣bot更新日志
=====================
新增：
[pcr_duel] 贵族决斗DLC
[pcrjjc] 竞技场推送（暂不支持私聊）
[schedule]日程查询（测试）
[portune]每日运势（测试）
更新：
[gacha]卡池更新 
[clanrank]上游更新
遗留：
[chat]语言库待完善
[pcrmemorygames]小游戏的怪物图鉴待完善
=====================
如有建议请使用[来杯咖啡 + 建议]。
'''.strip()

@sv.on_fullmatch(('botlog', '更新日志', '优衣更新日志', '优衣log'), only_to_me=False)
async def update_log(bot, ev):
    await bot.send(ev, LOG)