"""
PCR会战管理命令 v2
猴子也会用的会战管理
命令设计遵循以下原则：
- 中文：降低学习成本
- 唯一：There should be one-- and preferably only one --obvious way to do it.
- 耐草：参数不规范时尽量执行
"""

import os
from datetime import datetime, timedelta
from typing import List
import matplotlib as mpl
from matplotlib import pyplot as plt
try:
    import ujson as json
except:
    import json

from aiocqhttp.exceptions import ActionFailed
from nonebot import NoneBot
from nonebot import MessageSegment as ms
from nonebot.typing import Context_T
from hoshino import util, priv

from . import sv, cb_cmd
from .argparse import ArgParser, ArgHolder, ParseResult
from .argparse.argtype import *
from .battlemaster import BattleMaster
from .exception import *

#plt.style.use('seaborn-pastel')
#mpl.rcParams['font.family'] = ['SimHei']
plt.rcParams['font.sans-serif'] = ['SimHei']
#mpl.rcParams['font.serif'] = ['Microsoft YaHei', 'DejaVu Serif']
plt.rcParams['axes.unicode_minus'] = False

USAGE_ADD_CLAN = '!建会 N公会名 S服务器代号'
USAGE_ADD_MEMBER = '!入会 昵称 (@qq)'
USAGE_LIST_MEMBER = '!查看成员'

USAGE_TIP = '\n\n※无需输入尖括号，圆括号内为可选参数'

ERROR_CLAN_NOTFOUND = f'公会未初始化：请*群管理*使用【{USAGE_ADD_CLAN}】进行初始化{USAGE_TIP}'
ERROR_ZERO_MEMBER = f'公会内无成员：使用【{USAGE_ADD_MEMBER}】以添加{USAGE_TIP}'
ERROR_MEMBER_NOTFOUND = f'未找到成员：请使用【{USAGE_ADD_MEMBER}】加入公会{USAGE_TIP}'
ERROR_PERMISSION_DENIED = '权限不足：需*群管理*以上权限'
ERROR_NOT_SUPERUSER = '权限不足：需机器人管理员'


def _check_clan(bm:BattleMaster):
    clan = bm.get_clan(1)
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    return clan

def _check_member(bm:BattleMaster, uid:int, alt:int, tip=None):
    mem = bm.get_member(uid, alt) or bm.get_member(uid, 0) # 兼容cmdv1
    if not mem:
        raise NotFoundError(tip or ERROR_MEMBER_NOTFOUND)
    return mem

def _check_admin(event:Context_T, tip:str=''):
    if not priv.check_priv(event, priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED + tip)

def _check_superuser(event:Context_T, tip:str=''):
    if not priv.check_priv(event, priv.SUPERUSER):
        raise PermissionDeniedError(ERROR_NOT_SUPERUSER + tip)


@cb_cmd('建会', ArgParser(usage=USAGE_ADD_CLAN, arg_dict={
        'N': ArgHolder(tip='公会名'),
        'S': ArgHolder(tip='服务器地区', type=server_code)}))
async def add_clan(bot:NoneBot, event:Context_T, args:ParseResult):
    _check_admin(event)
    bm = BattleMaster(event['group_id'])
    if bm.has_clan(1):
        bm.mod_clan(1, args.N, args.S)
        await bot.send(event, f'公会信息已修改！\n{args.N} {server_name(args.S)}', at_sender=True)
    else:
        bm.add_clan(1, args.N, args.S)
        await bot.send(event, f'公会建立成功！{args.N} {server_name(args.S)}', at_sender=True)


@cb_cmd('查看公会', ArgParser('!查看公会'))
async def list_clan(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clans = bm.list_clan()
    if len(clans):
        clans = map(lambda x: f"{x['cid']}会：{x['name']} {server_name(x['server'])}", clans)
        msg = ['本群公会：', *clans]
        await bot.send(event, '\n'.join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)


@cb_cmd('入会', ArgParser(usage=USAGE_ADD_MEMBER, arg_dict={
        '': ArgHolder(tip='昵称', default=''),
        '@': ArgHolder(tip='qq号', type=int, default=0)}))
async def add_member(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    uid = args['@'] or args.at or event['user_id']
    name = args['']
    if uid != event['user_id']:
        _check_admin(event, '才能添加其他人')
        try:    # 尝试获取群员信息，用以检查该成员是否在群中
            await bot.get_group_member_info(self_id=event['self_id'], group_id=bm.group, user_id=uid)
        except:
            raise NotFoundError(f'Error: 无法获取群员信息，请检查{uid}是否属于本群')
    if not name:
        m = await bot.get_group_member_info(self_id=event['self_id'], group_id=bm.group, user_id=uid)
        name = m['card'] or m['nickname'] or str(m['user_id'])

    mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0)     # 兼容cmdv1
    if mem:
        bm.mod_member(uid, mem['alt'], name, 1)
        await bot.send(event, f'成员{ms.at(uid)}昵称已修改为{name}')
    else:
        bm.add_member(uid, bm.group, name, 1)
        await bot.send(event, f"成员{ms.at(uid)}添加成功！欢迎{name}加入{clan['name']}")


@cb_cmd(('查看成员', '成员查看', '查询成员', '成员查询'), ArgParser(USAGE_LIST_MEMBER))
async def list_member(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    mems = bm.list_member(1)
    if l := len(mems):
        # 数字太多会被腾讯ban
        mems = map(lambda x: '{uid: <11,d} | {name}'.format_map(x), mems)
        msg = [ f"\n{clan['name']}   {l}/30 人\n____ QQ ____ | 昵称", *mems]
        await bot.send(event, '\n'.join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_ZERO_MEMBER)


@cb_cmd('退会', ArgParser(usage='!退会 (@qq)', arg_dict={
        '@': ArgHolder(tip='qq号', type=int, default=0)}))
async def del_member(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    uid = args['@'] or args.at or event['user_id']
    mem = _check_member(bm, uid, bm.group, '公会内无此成员')
    if uid != event['user_id']:
        _check_admin(event, '才能踢人')
    bm.del_member(uid, mem['alt'])
    await bot.send(event, f"成员{mem['name']}已从公会删除", at_sender=True)


@cb_cmd('清空成员', ArgParser('!清空成员'))
async def clear_member(bot:NoneBot, event:Context_T, args:ParseResult):
    # Dangerous operation. Banned temporarily.
    await bot.send(event, "危险功能，暂时禁用", at_sender=True)
    return

    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    _check_admin(event)
    msg = f"{clan['name']}已清空！" if bm.clear_member(1) else f"{clan['name']}已无成员"
    await bot.send(event, msg, at_sender=True)


@cb_cmd('一键入会', ArgParser('!一键入会'))
async def batch_add_member(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    _check_admin(event)
    try:
        mlist = await bot.get_group_member_list(self_id=event['self_id'], group_id=bm.group)
    except ActionFailed:
        raise ClanBattleError('Bot缓存未更新，暂时无法使用一键入会。请尝试【!入会】命令逐个添加')
    if len(mlist) > 50:
        raise ClanBattleError('群员过多！一键入会仅限50人以内群使用')

    self_id = event['self_id']
    succ, fail = 0, 0
    for m in mlist:
        if m['user_id'] != self_id:
            try:
                bm.add_member(m['user_id'], bm.group, m['card'] or m['nickname'] or str(m['user_id']), 1)
                succ += 1
            except DatabaseError:
                fail += 1
    msg = f'批量注册完成！成功{succ}/失败{fail}\n使用【{USAGE_LIST_MEMBER}】查看当前成员列表'
    await bot.send(event, msg, at_sender=True)


def _gen_progress_text(clan_name, round_, boss, hp, max_hp, score_rate):
    return f"{clan_name} 当前进度：\n{round_}周目 {BattleMaster.int2kanji(boss)}王    SCORE x{score_rate:.1f}\nHP={hp:,d}/{max_hp:,d}"


async def process_challenge(bot:NoneBot, event:Context_T, ch:ParseResult):
    """
    处理一条报刀 需要保证challenge['flag']的正确性
    """

    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    mem = _check_member(bm, ch.uid, ch.alt)

    cur_round, cur_boss, cur_hp = bm.get_challenge_progress(1, now)
    round_ = ch.round or cur_round
    boss = ch.boss or cur_boss
    damage = ch.damage if ch.flag != BattleMaster.LAST else (ch.damage or cur_hp)
    flag = ch.flag

    if (ch.flag == BattleMaster.LAST) and (ch.round or ch.boss) and (not damage):
        raise NotFoundError('补报尾刀请给出伤害值')     # 补报尾刀必须给出伤害值

    msg = ['']
    if round_ != cur_round or boss != cur_boss:
        msg.append('⚠️上报与当前进度不一致')
    else:   # 伤害校对
        eps = 30000
        if damage > cur_hp + eps:
            damage = cur_hp
            msg.append(f'⚠️过度虐杀 伤害数值已自动修正为{damage}')
            if flag == BattleMaster.NORM:
                flag = BattleMaster.LAST
                msg.append('⚠️已自动标记为尾刀')
        elif flag == BattleMaster.LAST:
            if damage < cur_hp - eps:
                msg.append('⚠️尾刀伤害不足 请未报刀成员及时上报')
            elif damage < cur_hp:
                if damage % 1000 == 0:
                    damage = cur_hp
                    msg.append(f'⚠️尾刀伤害已自动修正为{damage}')
                else:
                    msg.append('⚠️Boss仍有少量残留血量')

    eid = bm.add_challenge(mem['uid'], mem['alt'], round_, boss, damage, flag, now)
    aft_round, aft_boss, aft_hp = bm.get_challenge_progress(1, now)
    max_hp, score_rate = bm.get_boss_info(aft_round, aft_boss, clan['server'])
    msg.append(f"记录编号E{eid}：\n{mem['name']}给予{round_}周目{bm.int2kanji(boss)}王{damage:,d}点伤害\n")
    msg.append(_gen_progress_text(clan['name'], aft_round, aft_boss, aft_hp, max_hp, score_rate))
    await bot.send(event, '\n'.join(msg), at_sender=True)

    # 判断是否更换boss，呼叫预约
    if aft_round != cur_round or aft_boss != cur_boss:
        if boss==5:
            boss = 6
        await call_subscribe(bot, event, aft_round, aft_boss)
    elif aft_boss == 5:
        threshold = bm.get_phase2_threshold(aft_round,clan['server'])
        if cur_hp >= threshold and aft_hp < threshold:
            aft_boss = 6
            await call_subscribe(bot, event, aft_round, aft_boss)
        elif cur_hp < threshold:
            boss = 6

    #await auto_unlock_boss(bot, event, bm)
    await auto_unsubscribe(bot, event, bm.group, mem['uid'], boss)


@cb_cmd(('出刀', '报刀'), ArgParser(usage='!出刀 <伤害值> (@qq) (R周目数) (B编号)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    '@': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    zone = bm.get_timezone_num(clan['server'])
    now = datetime.now()

    uid = args['@'] or args.at or event['user_id']
    alt = event['group_id']
    challen = bm.list_challenge_of_user_of_day(uid, alt, now, zone)

    flg = BattleMaster.NORM
    if len(challen)>0 and (challen[-1]['flag'] & BattleMaster.LAST):
        await bot.send(event, '已自动识别为补时刀', at_sender=True)
        flg = BattleMaster.EXT

    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': uid,
        'alt': alt,
        'flag': flg
    })
    await process_challenge(bot, event, challenge)


@cb_cmd(('出尾刀', '收尾', '尾刀'), ArgParser(usage='!出尾刀 (<伤害值>) (@<qq号>)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int, default=0),
    '@': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_last(bot:NoneBot, event:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args['@'] or args.at or event['user_id'],
        'alt': event['group_id'],
        'flag': BattleMaster.LAST
    })
    await process_challenge(bot, event, challenge)


@cb_cmd(('出补时刀', '补时刀', '补时', '出补偿刀', '补偿刀', '补偿'), ArgParser(usage='!出补时刀 <伤害值> (@qq)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    '@': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_ext(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    zone = bm.get_timezone_num(clan['server'])
    now = datetime.now()

    uid = args['@'] or args.at or event['user_id']
    alt = event['group_id']
    challen = bm.list_challenge_of_user_of_day(uid, alt, now, zone)

    if len(challen)==0 or not (challen[-1]['flag'] & BattleMaster.LAST):
        await bot.send(event, '⚠️您的上一刀不是尾刀！', at_sender=True)
        return

    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args['@'] or args.at or event['user_id'],
        'alt': event['group_id'],
        'flag': BattleMaster.EXT
    })
    await process_challenge(bot, event, challenge)


@cb_cmd(('掉刀','滑刀','吞刀'), ArgParser(usage='!掉刀 (@qq)', arg_dict={
    '@': ArgHolder(tip='qq号', type=int, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_timeout(bot:NoneBot, event:Context_T, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': 0,
        'uid': args['@'] or args.at or event['user_id'],
        'alt': event['group_id'],
        'flag': BattleMaster.TIMEOUT
    })
    await process_challenge(bot, event, challenge)


@cb_cmd(('删刀','撤销','删除报刀','撤销出刀','删除出刀'), ArgParser(usage='!删刀 E记录编号', arg_dict={
    'E': ArgHolder(tip='记录编号', type=int)}))
async def del_challenge(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    ch = bm.get_challenge(args.E, 1, now)
    if not ch:
        raise NotFoundError(f'未找到出刀记录E{args.E}')
    if ch['uid'] != event['user_id']:
        _check_admin(event, '才能删除其他人的记录')
    bm.del_challenge(args.E, 1, now)
    await bot.send(event, f"{clan['name']}已删除出刀记录E{args.E}", at_sender=True)

@cb_cmd(('改刀','修改出刀','更改出刀'), ArgParser(usage='''!改刀 E记录编号 (T时间) (D伤害) (B编号) (R周目数) (@qq) (F类型)
!改刀 E1 T2020-7-1-12:00:00 B3 R4 D750000''', arg_dict={
    'E': ArgHolder(tip='记录编号', type=int),
    'T': ArgHolder(tip='时间', type=str, default=''),
    'D': ArgHolder(tip='伤害', type=damage_int, default=-1),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'F': ArgHolder(tip='类型', type=str, default='不变'),
    '@': ArgHolder(tip='QQ号', type=int, default=0)
    }))
async def change_challenge(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    ch = bm.get_challenge(args.E, 1, now)
    if not ch:
        raise NotFoundError(f'未找到出刀记录E{args.E}')
    if ch['uid'] != event['user_id']:
        _check_admin(event, '才能修改其他人的记录')

    eid = ch['eid']
    uid = args.at or args['@'] or ch['uid']
    alt = ch['alt']
    rnd = ch['round'] if args['R']==0 else args['R']
    boss = ch['boss'] if args['B']==0 else args['B']
    dmg = ch['dmg'] if args['D']==-1 else args['D']

    flag = ch['flag']
    flg = args['F']
    if flg!='不变':
        if flg in ('通常','普通','通常刀','普通刀'):
            flag = BattleMaster.NORM
        elif flg in ('尾刀','收尾','收尾刀'):
            flag = BattleMaster.LAST
        elif flg in ('补时','补时刀','补刀'):
            flag = BattleMaster.EXT
        elif flg in ('掉刀','滑刀','吞刀'):
            flag = BattleMaster.TIMEOUT
        else:
            raise NotFoundError(f'未知的参数"{flg}"')

    time = ch['time']
    if args['T']!='':
        try:
            time = datetime.strptime(args['T'],'%Y-%m-%d-%H:%M:%S')
        except:
            await bot.send(event, f'时间参数错误：应为"YYYY-MM-DD-hh:mm:ss"格式')
            return

    bm.mod_challenge(eid,uid,alt,rnd,boss,dmg,flag,time)
    await bot.send(event, f"{clan['name']}已修改出刀记录E{args.E}", at_sender=True)

@cb_cmd(('查看出刀',), ArgParser(usage='!查看出刀', arg_dict={
    'E': ArgHolder(tip='记录编号', type=int)
    }))
async def print_challenge(bot:NoneBot, event:Context_T, args:ParseResult):
    _check_superuser(event, '才能使用此测试功能')
    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    ch = bm.get_challenge(args.E, 1, now)
    if not ch:
        raise NotFoundError(f'未找到出刀记录E{args.E}')

    await bot.send(event, f'测试信息\n{ch}')

# TODO 将预约信息转至数据库
SUBSCRIBE_PATH = os.path.expanduser('~/.hoshino/clanbattle_sub/')
SUBSCRIBE_MAX = [99, 6, 6, 6, 6, 6]
os.makedirs(SUBSCRIBE_PATH, exist_ok=True)

class SubscribeData:

    def __init__(self, data:dict):
        for i in '123456':
            data.setdefault(i, [])
            data.setdefault('m' + i, [])
            l = len(data[i])
            if len(data['m' + i]) != l:
                data['m' + i] = [None] * l
        data.setdefault('tree', [])
        data.setdefault('lock', [])
        if 'max' not in data or len(data['max']) != 7:
            data['max'] = [99, 10, 10, 10, 10, 10, 10]
        self._data = data
        
    @staticmethod
    def default():
        return SubscribeData({
            '1':[], '2':[], '3':[], '4':[], '5':[], '6':[],
            'm1':[], 'm2':[], 'm3':[], 'm4':[], 'm5':[], 'm6':[],
            'tree':[], 'lock':[],
            'max': [99, 10, 10, 10, 10, 10, 10]
        })
    
    def get_sub_list(self, boss:int):
        return self._data[str(boss)]
        
    def get_memo_list(self, boss:int):
        return self._data[f'm{boss}']
    
    def get_tree_list(self):
        return self._data['tree']

    def get_sub_limit(self, boss:int):
        return self._data['max'][boss]

    def set_sub_limit(self, boss:int, limit:int):
        self._data['max'][boss] = limit

    def add_sub(self, boss:int, uid:int, memo:str):
        self._data[str(boss)].append(uid)
        self._data[f'm{boss}'].append(memo)

    def remove_sub(self, boss:int, uid:int):
        s = self._data[str(boss)]
        m = self._data[f'm{boss}']
        i = s.index(uid)
        s.pop(i)
        m.pop(i)

    def add_tree(self, uid:int):
        self._data['tree'].append(uid)

    def remove_tree(self, uid:int):
        try:
            self._data['tree'].remove(uid)
        except:
            pass
        
    def clear_tree(self):
        self._data['tree'].clear()
        
    def get_lock_info(self):
        return self._data['lock']
    
    def set_lock(self, uid:int, ts):
        self._data['lock'] = [ (uid, ts) ]

    def clear_lock(self):
        self._data['lock'].clear()

    def dump(self, filename):
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(self._data, f, ensure_ascii=False)


def _load_sub(gid) -> SubscribeData:
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8') as f:
            return SubscribeData(json.load(f))
    else:
        return SubscribeData.default()


def _save_sub(sub:SubscribeData, gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    sub.dump(filename)


def _gen_namelist_text(bm:BattleMaster, uidlist:List[int], memolist:List[str]=None, do_at=False):
    if do_at:
        mems = map(lambda x: str(ms.at(x)), uidlist)
    else:
        mems = map(lambda x: bm.get_member(x, bm.group) or bm.get_member(x, 0) or {'name': str(x)}, uidlist)
        mems = map(lambda x: x['name'], mems)
    if memolist:
        mems = list(mems)
        for i in range(len(mems)):
            if i < len(memolist) and memolist[i]:
                mems[i] = f"{mems[i]}：{memolist[i]}"
    return mems


SUBSCRIBE_TIP = ''

@cb_cmd('预约', ArgParser(usage='!预约 <Boss号> [M留言] [狂暴]', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code),
    'M': ArgHolder(tip='留言', default=''),
    '狂' : ArgHolder(tip='状态', type=str, default='')}))
async def subscribe(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    uid = event['user_id']
    _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    boss = args['']

    if args['狂'] not in ('','暴'):
        await bot.send(event, 'Boss状态错误！', at_sender=True)
        return
    elif args['狂']=='暴':
        if boss!=5:
            await bot.send(event, '只有五王存在狂暴状态！', at_sender=True)
            return
        boss=6

    memo = args.M
    boss_name = bm.int2kanji(boss)
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    limit = sub.get_sub_limit(boss)
    if uid in slist:
        raise AlreadyExistError(f'您已经预约过{boss_name}王了')
    msg = ['']
    if len(slist) < limit:
        sub.add_sub(boss, uid, memo)
        _save_sub(sub, bm.group)
        msg.append(f'已为您预约{boss_name}王！')
    else:
        msg.append(f'预约失败：{boss_name}王预约人数已达上限')
    msg.append(f'=== 当前队列 {len(slist)}/{limit} ===')
    msg.extend(_gen_namelist_text(bm, slist, mlist))
    msg.append(SUBSCRIBE_TIP)
    await bot.send(event, '\n'.join(msg), at_sender=True)


@cb_cmd(('取消预约', '预约取消'), ArgParser(usage='!取消预约 <Boss号> [狂暴]', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code),
    '狂': ArgHolder(tip='状态', type=str, default='')}))
async def unsubscribe(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    uid = event['user_id']
    _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    boss = args['']

    if args['狂'] not in ('','暴'):
        await bot.send(event, 'Boss状态错误！', at_sender=True)
        return
    elif args['狂']=='暴':
        if boss!=5:
            await bot.send(event, '只有五王存在狂暴状态！', at_sender=True)
            return
        boss=6

    boss_name = bm.int2kanji(boss)    
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    limit = sub.get_sub_limit(boss)    
    if uid not in slist:
        raise NotFoundError(f'您没有预约{boss_name}王')
    sub.remove_sub(boss, uid)
    _save_sub(sub, bm.group)
    msg = [ f'\n已为您取消预约{boss_name}王！' ]
    msg.append(f'=== 当前队列 {len(slist)}/{limit} ===')    
    msg.extend(_gen_namelist_text(bm, slist, mlist))
    await bot.send(event, '\n'.join(msg), at_sender=True)


async def auto_unsubscribe(bot:NoneBot, event:Context_T, gid, uid, boss):
    sub = _load_sub(gid)
    slist = sub.get_sub_list(boss)
    if uid not in slist:
        return
    sub.remove_sub(boss, uid)
    _save_sub(sub, gid)
    await bot.send(event, f'已为{ms.at(uid)}自动取消{BattleMaster.int2kanji(boss)}王的订阅')


async def call_subscribe(bot:NoneBot, event:Context_T, round_:int, boss:int):
    bm = BattleMaster(event['group_id'])
    msg = []
    sub = _load_sub(bm.group)
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    tlist = sub.get_tree_list()
    if slist:
        msg.append(f"您预约的{BattleMaster.int2kanji(boss)}王出现啦！")
        msg.extend(_gen_namelist_text(bm, slist, mlist, do_at=True))
    if slist and tlist and boss!=6:
        msg.append("==========")
    if tlist and boss!=6:
        msg.append(f"以下成员可以下树了")
        msg.extend(map(lambda x: str(ms.at(x)), tlist))
        sub.clear_tree()
        _save_sub(sub, bm.group)
    if msg:
        await bot.send(event, '\n'.join(msg), at_sender=False)    # do not at the sender


@cb_cmd(('查询预约', '预约查询', '查看预约', '预约查看'), ArgParser('!查询预约'))
async def list_subscribe(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    msg = [ f"\n{clan['name']}当前预约情况：" ]
    sub = _load_sub(bm.group)
    for boss in range(1, 7):
        slist = sub.get_sub_list(boss)
        mlist = sub.get_memo_list(boss)
        limit = sub.get_sub_limit(boss)
        msg.append(f"========\n{bm.int2kanji(boss)}王: {len(slist)}/{limit}")
        msg.extend(_gen_namelist_text(bm, slist, mlist))
    await bot.send(event, '\n'.join(msg), at_sender=True)


@cb_cmd(('清空预约', '预约清空', '清理预约', '预约清理'), ArgParser('!清空预约 <Boss编号> [狂暴]', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code),
    '狂': ArgHolder(tip='状态', type=str, default='')}))
async def clear_subscribe(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    _check_admin(event, '才能清理预约队列')
    sub = _load_sub(bm.group)
    boss = args['']

    if args['狂'] not in ('','暴'):
        await bot.send(event, 'Boss状态错误！', at_sender=True)
        return
    elif args['狂']=='暴':
        if boss!=5:
            await bot.send(event, '只有五王存在狂暴状态！', at_sender=True)
            return
        boss=6
    
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    if slist:
        slist.clear()
        mlist.clear()
        _save_sub(sub, bm.group)
        await bot.send(event, f"{bm.int2kanji(boss)}王预约队列已清空", at_sender=True)
    else:
        raise NotFoundError(f"无人预约{bm.int2kanji(boss)}王")


@cb_cmd(('预约上限', ), ArgParser(usage='!预约上限 B<Boss号> <上限值>', arg_dict={
    'B': ArgHolder(tip='Boss编号', type=boss_code),
    '': ArgHolder(tip='上限值', type=int)
}))
async def set_subscribe_limit(bot:NoneBot, event, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    _check_admin(event, '才能设置预约上限')
    limit = args['']
    if not (0 < limit <= 30):
        raise ClanBattleError('预约上限只能为1~30内的整数')
    sub = _load_sub(bm.group)
    sub.set_sub_limit(args.B, limit)    
    _save_sub(sub, bm.group)
    await bot.send(event, f'{bm.int2kanji(args.B)}王预约上限已设置为：{limit}')


@cb_cmd(('挂树', '上树'), ArgParser('!挂树'))
async def add_sos(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    uid = event['user_id']
    clan = _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    tree = sub.get_tree_list()
    if uid in tree:
        raise AlreadyExistError("您已在树上")
    sub.add_tree(uid)
    _save_sub(sub, bm.group)
    msg = [ "\n您已上树，本Boss被击败时将会通知您",
           f"目前{clan['name']}挂树人数为{len(tree)}人：" ]
    msg.extend(_gen_namelist_text(bm, tree))
    await bot.send(event, '\n'.join(msg), at_sender=True)


@cb_cmd(('下树', '取消挂树'), ArgParser('!下树'))
async def remove_sos(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    uid = event['user_id']
    clan = _check_clan(bm)
    _check_member(bm, uid, bm.group)
    sub = _load_sub(bm.group)
    tree = sub.get_tree_list()
    if uid not in tree:
        raise AlreadyExistError("您不在树上")
    sub.remove_tree(uid)
    _save_sub(sub, bm.group)
    msg = [ "\n您已下树",
           f"目前{clan['name']}挂树人数为{len(tree)}人：" ]
    msg.extend(_gen_namelist_text(bm, tree))
    await bot.send(event, '\n'.join(msg), at_sender=True)


@cb_cmd(('查树', ), ArgParser('!查树'))
async def list_sos(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    sub = _load_sub(bm.group)
    tree = sub.get_tree_list()
    msg = [ f"\n目前{clan['name']}挂树人数为{len(tree)}人：" ]
    msg.extend(_gen_namelist_text(bm, tree))
    await bot.send(event, '\n'.join(msg), at_sender=True)

'''
@cb_cmd(('锁定', '申请出刀'), ArgParser('!锁定'))
async def lock_boss(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    _check_clan(bm)
    _check_member(bm, event['user_id'], bm.group)
    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0) or {'name': str(uid)}
        delta = datetime.now() - time
        delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
        msg = f"\n锁定失败：{mem['name']}已于{delta}前锁定了Boss"
        await bot.send(event, msg, at_sender=True)
    else:
        uid = event['user_id']
        time = datetime.now()
        sub.set_lock(uid, datetime.now().timestamp())
        _save_sub(sub, bm.group)
        msg = f"已锁定Boss"
        await bot.send(event, msg, at_sender=True)
@cb_cmd(('解锁', ), ArgParser('!解锁'))
async def unlock_boss(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    _check_clan(bm)
    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        if uid != event['user_id']:
            mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0) or {'name': str(uid)}
            delta = datetime.now() - time
            delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
            _check_admin(event, f"才能解锁其他人\n解锁失败：{mem['name']}于{delta}前锁定了Boss")
        sub.clear_lock()
        _save_sub(sub, bm.group)
        msg = f"\nBoss已解锁"
        await bot.send(event, msg, at_sender=True)
    else:
        msg = "\n无人锁定Boss"
        await bot.send(event, msg, at_sender=True)
async def auto_unlock_boss(bot:NoneBot, event:Context_T, bm:BattleMaster):
    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        if uid != event['user_id']:
            mem = bm.get_member(uid, bm.group) or bm.get_member(uid, 0) or {'name': str(uid)}
            delta = datetime.now() - time
            delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
            msg = f"⚠️{mem['name']}于{delta}前锁定了Boss，您出刀前未申请锁定！"
            await bot.send(event, msg, at_sender=True)
        else:
            sub.clear_lock()
            _save_sub(sub, bm.group)
            msg = f"\nBoss已自动解锁"
            await bot.send(event, msg, at_sender=True)
'''


@cb_cmd(('进度', '进度查询', '查询进度', '进度查看', '查看进度', '状态'), ArgParser(usage='!进度'))
async def show_progress(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    r, b, hp = bm.get_challenge_progress(1, datetime.now())
    max_hp, score_rate = bm.get_boss_info(r, b, clan['server'])
    msg = _gen_progress_text(clan['name'], r, b, hp, max_hp, score_rate)
    await bot.send(event, '\n' + msg, at_sender=True)


@cb_cmd(('统计', '伤害统计'), ArgParser(usage='!伤害统计'))
async def stat_damage(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_damage(1, now)

    yn = len(stat)
    if not yn:
        await bot.send(event, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    stat.sort(key=lambda x: x[3][0], reverse=True)
    name = [ s[2] for s in stat ]
    y_pos = list(range(yn))
    y_size = 0.3 * yn + 1.0
    unit = 1e4
    unit_str = 'w'

    # convert to pre-sum
    for s in stat:
        d = s[3]
        d[0] = 0
        for i in range(2, 6):
            d[i] += d[i - 1]
    pre_sum_dmg = [
        [ s[3][b] for s in stat ] for b in range(6)
    ]

    # generate statistic figure
    fig, ax = plt.subplots()
    fig.set_size_inches(10, y_size)
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战伤害统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel('伤害')
    colors = ['#00a2e8', '#22b14c', '#b5e61d', '#fff200', '#ff7f27', '#ed1c24']
    bars = [ ax.barh(y_pos, pre_sum_dmg[b], align='center', color=colors[b]) for b in range(5, -1, -1) ]
    bars.reverse()
    ax.ticklabel_format(axis='x', style='plain')
    for b in range(1, 6):
        for i, rect in enumerate(bars[b]):
            x = (rect.get_width() + bars[b - 1][i].get_width()) / 2
            y = rect.get_y() + rect.get_height() / 2
            d = pre_sum_dmg[b][i] - pre_sum_dmg[b - 1][i]
            if d > unit:
                ax.text(x, y, f'{d/unit:.0f}{unit_str}', ha='center', va='center')
    plt.subplots_adjust(left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size)
    pic = util.fig2b64(plt)
    plt.close()
    
    msg = f"{ms.image(pic)}\n※分数统计请发送“!分数统计”"
    await bot.send(event, msg, at_sender=True)


@cb_cmd('分数统计', ArgParser(usage='!分数统计'))
async def stat_score(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    now = datetime.now()
    clan = _check_clan(bm)
    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_score(1, now)
    stat.sort(key=lambda x: x[3], reverse=True)
    
    if not len(stat):
        await bot.send(event, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    # msg = [ f"\n{yyyy}年{mm}月会战{clan['name']}分数统计：" ]
    # for _, _, name, score in stat:
    #     score = f'{score:,d}'           # 数字太多会被腾讯ban，用逗号分隔
    #     blank = '  ' * (11-len(score))  # QQ字体非等宽，width(空格*2) == width(数字*1)
    #     msg.append(f"{blank}{score}分 | {name}")

    # generate statistic figure
    fig, ax = plt.subplots()
    score = list(map(lambda i: i[3], stat))
    yn = len(stat)
    name = list(map(lambda i: i[2], stat))
    y_pos = list(range(yn))

    if score[0] >= 1e8:
        unit = 1e8
        unit_str = 'e'
    else:
        unit = 1e4
        unit_str = 'w'

    y_size = 0.3 * yn + 1.0
    fig.set_size_inches(10, y_size)
    bars = ax.barh(y_pos, score, align='center')
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战分数统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel('分数')
    ax.ticklabel_format(axis='x', style='plain')
    for rect in bars:
        w = rect.get_width()
        ax.text(w, rect.get_y() + rect.get_height() / 2, f'{w/unit:.2f}{unit_str}', ha='left', va='center')
    plt.subplots_adjust(left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size)
    pic = util.fig2b64(plt)
    plt.close()

    msg = f"{ms.image(pic)}\n※伤害统计请发送“!伤害统计”"
    await bot.send(event, msg, at_sender=True)


async def _do_show_remain(bot:NoneBot, event:Context_T, args:ParseResult, at_user:bool):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)
    if at_user:
        _check_admin(event, '才能催刀。您可以用【!查刀】查询余刀')

    today = args[''] if not at_user else '今日'
    if today not in ('昨日','今日'):
        await bot.send(event, f'无法识别参数“{today}”\n如果您要设置阈值，请使用“T<阈值>”',at_sender=True)
        return

    threshold = args['T'] or 1
    if threshold > 3 or threshold < 1:
        threshold = 1
    cnt = 0
    people = 0
    rlist = bm.list_challenge_remain(1, datetime.now() if today=='今日' else datetime.now()-timedelta(days=1))
    rlist.sort(key=lambda x: x[3] + x[4], reverse=True)
    msg = [  ('' if at_user else '\n') + f"{clan['name']}{today}余刀：" ]
    for uid, _, name, r_n, r_e in rlist:
        if r_n + r_e >= threshold:
            msg.append(f"剩{r_n}刀 补时{r_e}刀 | {ms.at(uid) if at_user else name}")
            cnt += r_n + r_e
            people += 1
    if len(msg) == 1:
        await bot.send(event, f"{today}{clan['name']}所有成员均已下班！各位辛苦了！", at_sender=True)
    else:
        msg.append(f'共剩{people}人{cnt}刀')
        if at_user:
            msg.append("=========\n"+args.M)
        await bot.send(event, '\n'.join(msg), at_sender=not at_user) # 催刀不需要at自己


@cb_cmd('查刀', ArgParser(usage='!查刀 (T阈值) (昨日)', arg_dict={
    'T': ArgHolder(tip='阈值', type=int, default=1),
    '@': ArgHolder(tip='qq号', type=int, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    '' : ArgHolder(tip='昨日', type=str, default='今日')}))
async def list_remain(bot:NoneBot, event:Context_T, args:ParseResult):
    if args['B'] or args['R'] or args['@'] or args.at:
        await list_challenge(bot,event,args)
    else:
        await _do_show_remain(bot, event, args, at_user=False)

@cb_cmd('催刀', ArgParser(usage='!催刀 (T阈值) (M留言)', arg_dict={
    'T': ArgHolder(tip='阈值', type=int, default=1),
    'M': ArgHolder(tip='留言', type=str, default='在？阿sir喊你出刀啦！')}))
async def urge_remain(bot:NoneBot, event:Context_T, args:ParseResult):
    await _do_show_remain(bot, event, args, at_user=True)


@cb_cmd('出刀记录', ArgParser(usage='!出刀记录 (@qq) (B编号) (R周目数) (昨日)', arg_dict={
        '@': ArgHolder(tip='qq号', type=int, default=0),
        'B': ArgHolder(tip='Boss编号', type=boss_code, default=0),
        'R': ArgHolder(tip='周目数', type=round_code, default=0),
        '' : ArgHolder(type=str, default='今日')}))
async def list_challenge(bot:NoneBot, event:Context_T, args:ParseResult):
    bm = BattleMaster(event['group_id'])
    clan = _check_clan(bm)

    today = args['']
    if today not in ('昨日','今日'):
        await bot.send(event, f'无法识别参数“{today}”', at_sender=True)
        return
    now = datetime.now() if today=='今日' else datetime.now()-timedelta(days=1)

    zone = bm.get_timezone_num(clan['server'])
    uid = args['@'] or args.at
    boss = args.B
    rnd = args.R
    if uid:
        mem = _check_member(bm, uid, bm.group, '公会内无此成员')
        challen = bm.list_challenge_of_user_of_day(mem['uid'], mem['alt'], now, zone)
    else:
        challen = bm.list_challenge_of_day(clan['cid'], now, zone)

    msg = [ f'{clan["name"]}出刀记录：\n编号|出刀者|周目|Boss|伤害|标记' ]
    challenstr = 'E{eid:0>3d}|{name}|r{round}|b{boss}|{dmg: >7,d}{flag_str}'
    for c in challen:
        if boss!=0 and boss!=c['boss']:
            continue
        if rnd!=0 and rnd!=c['round']:
            continue
        mem = bm.get_member(c['uid'], c['alt'])
        c['name'] = mem['name'] if mem else c['uid']
        flag = c['flag']
        c['flag_str'] = '|补时' if flag & bm.EXT else '|尾刀' if flag & bm.LAST else '|掉线' if flag & bm.TIMEOUT else '|通常'
        msg.append(challenstr.format_map(c))
    await bot.send(event, '\n'.join(msg))