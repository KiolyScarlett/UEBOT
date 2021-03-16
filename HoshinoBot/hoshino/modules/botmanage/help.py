from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

MANUAL = '''
=====================
- 草野优衣Bot使用说明 -
=====================
输入方括号[]内的关键词即可触发相应的功能
※注意其中的【空格】不可省略！
※部分功能必须手动at本bot才会触发(复制无效)
※※调教时请注意使用频率，您的滥用可能会导致bot账号被封禁
==================
- 公主连接Re:Dive -
==================
[@bot来发十连] 十连转蛋模拟
[@bot来发单抽] 单抽转蛋模拟
[@bot来一井] 4w5钻！买定离手！
[@bot妈] 给主さま盖章章
[查看卡池] 查看bot现在的卡池及出率
[公会排名abc] 查询公会名字包含abc的公会的排名
[怎么拆 妹弓] 后以空格隔开接角色名，查询竞技场解法
[pcr速查] 常用网址/速查表
[bcr速查] B服萌新攻略
[rank表] 查看rank推荐表
[黄骑充电表] 查询黄骑1动充电规律
[@bot官漫132] 官方四格阅览
[挖矿 15001] 查询矿场中还剩多少钻
[切噜一下] 后以空格隔开接想要转换为切噜语的话
[切噜～♪切啰巴切拉切蹦切蹦] 切噜语翻译
[xcw语音]  试听老婆们的语音
===========
- 通用功能 -
===========
[.r] 掷骰子
[.r 3d12] 掷3次12面骰子
[@bot精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
[给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
[@bot来杯咖啡] 联系维护组，空格后接反馈内容
=================
- 群管理限定功能 -
=================
[翻译 もう一度、キミとつながる物語] 机器翻译
[lssv] 查看功能模块的开关状态

发送以下关键词查看更多：
[帮助pcr查询]
[帮助pcr娱乐]
[帮助pcr订阅]
[帮助通用]

※※初次使用请仔细阅读帮助开头的注意事项
※※魔改by 渡渡鸟烤肉。。赞助by Mirror, 伊利西亚斯。。
※※图库更新时间 每天都在更
※※卡池更新时间2021年1月5日16:53:38。。
※※调教时请注意使用频率，您的滥用可能会导致bot账号被封禁
'''.strip()

def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for sv in service_list:
        if sv.visible:
            spit_line = '=' * max(0, 18 - len(sv.name))
            manual.append(f"|{'○' if sv.check_enabled(gid) else '×'}| {sv.name} {spit_line}")
            if sv.help:
                manual.append(sv.help)
    return '\n'.join(manual)


@sv.on_prefix(('help', '帮助', '幫助'))
async def send_help(bot, ev: CQEvent):
    bundle_name = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    if not bundle_name:
        await bot.send(ev, MANUAL)
    elif bundle_name in bundles:
        msg = gen_bundle_manual(bundle_name, bundles[bundle_name], ev.group_id)
        await bot.send(ev, msg)
    # else: ignore
