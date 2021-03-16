import random

from nonebot import on_command

from hoshino import R, Service, priv, util

# basic function for debug, not included in Service('chat')

@on_command('zai?', aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'), only_to_me=True)
async def say_hello(session):
    await session.send('はい！私はいつも貴方の側にいますよ！')

sv = Service('chat', visible=False)

@sv.on_fullmatch(('沙雕机器人', '沙雕機器人', '破机器人', '垃圾机器人'))
async def say_sorry(bot, ev):
    await bot.send(ev, 'ごめんなさい！嘤嘤嘤(〒︿〒)')

@sv.on_fullmatch(('机器人', 'bot'))
async def say_bot(bot, ev):
    await bot.send(ev, '酷q跑路了，其实我是会长30块一天请的，24小时高强度工作')    
    
@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, R.img('laopo.jpg').cqcode)
    else:
        await bot.send(ev, 'mua~')

@sv.on_fullmatch('老公', only_to_me=True)
async def chat_laogong(bot, ev):
    await bot.send(ev, '你给我滚！', at_sender=True)

@sv.on_fullmatch('mua', only_to_me=True)
async def chat_mua(bot, ev):
    await bot.send(ev, '笨蛋~', at_sender=True)

@sv.on_fullmatch('来点星奏', only_to_me=False)
async def seina(bot, ev):
    await bot.send(ev, R.img('星奏.png').cqcode)

@sv.on_fullmatch('我喜欢你', only_to_me=True)
async def chat_xihuan(bot, ev):
    await bot.send(ev, '对不起！我有别的骑士君了', at_sender=True)


@sv.on_fullmatch('喷水', only_to_me=True)
async def chat_penshui(bot, ev):
    await bot.send(ev, R.img('没吃饭吗弟弟.JPG').cqcode)

@sv.on_fullmatch('对不起', only_to_me=True)
async def chat_duibuqi(bot, ev):
    await bot.send(ev, R.img('是谁对不起ue.JPG').cqcode)
    
@sv.on_fullmatch(('我有个朋友说他好了', '我朋友说他好了'))
async def ddhaole(bot, ev):
    await bot.send(ev, '那个朋友是不是你弟弟？')
    await util.silence(ev, 30)

@sv.on_fullmatch(('hentai','变态'))
async def chat_biantai(bot, ev):
    if random.random() < 0.50:
        await bot.send(ev, R.img('hantai.jpg').cqcode)
    else:
        path = "C:/res/record/103611小仓唯/vo_adv_1036001_004.m4a"
        
        await bot.send(ev, f'[CQ:record,file=file:///{path}]')

@sv.on_fullmatch(('西内','系内','去死'))
async def chat_xine(bot, ev):
    if random.random() < 0.50:
        path = "C:/res/record/107111克总/vo_btl_107101_attack_003.m4a"
        await bot.send(ev, f'[CQ:record,file=file:///{path}]')

@sv.on_fullmatch(('妹弓UB','妹弓ub'))
async def chat_mgub(bot, ev):
    if random.random() < 0.50:
        path = "C:/res/record/101111妹弓/vo_btl_101161_ub.m4a"
        await bot.send(ev, f'[CQ:record,file=file:///{path}]')


@sv.on_fullmatch('我好了')
async def nihaole(bot, ev):
    await bot.send(ev, '不许好，憋回去！')
    await util.silence(ev, 30)

# ============================================ #

@sv.on_command('确实', aliases=('有一说一', 'u1s1', 'yysy'), only_to_me=False)
async def chat_queshi(session):
    if random.random() < 0.3:
        await session.send(R.img('确实.jpg').cqcode)
    elif random.random() > 0.6:
        await session.send('一，确实。')
        await util.silence(session.ctx, 30)

@sv.on_keyword(('好色', '好涩', '车神', 'loli', 'hso', 'lsp'))
async def chat_hso(bot, ev):
    if random.random() < 0.40:
        await bot.send(ev, '好色哦', at_sender=True)
        
@sv.on_keyword(('井了', '沉了'))
async def chat_jingle(bot, ev):
    if random.random() < 0.40:
        await bot.send(ev, '真可惜。不过不要灰心，说不定下一次抽卡就出奇迹了呢！', at_sender=True)
    elif random.random() > 0.40:
        await bot.send(ev,  R.img('没出货.jpg').cqcode)
        

@sv.on_keyword(('会战', '刀'))
async def chat_clanba(bot, ctx):
    if random.random() < 0.03:
        await bot.send(ctx, R.img('我的天啊你看看都几点了.jpg').cqcode)

@sv.on_keyword(('mcw', '猫仓唯', '喵仓唯'))
async def chat_mcw(bot, ctx):
    if random.random() < 0.30:
        await bot.send(ctx, R.img('mcw.gif').cqcode)
    


@sv.on_keyword(('内鬼'))
async def chat_neigui(bot, ctx):
    if random.random() < 0.30:
        await bot.send(ctx, R.img('内鬼.png').cqcode)
    elif random.random() > 0.6:
        await bot.send(ctx, R.img('内鬼2.jpg').cqcode)


@sv.on_keyword(('服了'))
async def chat_xianding(bot, ctx):
    if random.random() < 0.50:
        await bot.send(ctx, R.img('服了.jpg').cqcode)

@sv.on_keyword(('社保','射爆'))
async def chat_shebao(bot, ctx):
    if random.random() < 0.50:
        await bot.send(ctx, R.img('射爆.jpg').cqcode)

@sv.on_keyword(('限定','人权'))
async def chat_xianding(bot, ctx):
    if random.random() < 0.10:
        await bot.send(ctx, R.img('限定.jpg').cqcode)

@sv.on_keyword(('哭了','哭','555'))
async def chat_kule(bot, ctx):
    if random.random() < 0.30:
        await bot.send(ctx, R.img('哭了.png').cqcode)

@sv.on_keyword(('杀','鲨'))
async def chat_shale(bot, ctx):
    if random.random() < 0.30:
        await bot.send(ctx, R.img('鲨了.png').cqcode)



@sv.on_keyword(('难过','伤心','炎拳','好起来'))
async def chat_haoqilai(bot, ctx):
    if random.random() < 0.50:
        await bot.send(ctx, R.img('好起来的.png').cqcode)

@sv.on_keyword(('老婆'))
async def chat_laopo(bot, ctx):
    if not priv.check_priv(ev, priv.SUPERUSER):
        if random.random() < 0.5:
            await bot.send(ctx, R.img('喊谁老婆呢.jpg').cqcode)
        else:
            await bot.send(ctx, R.img('老婆真人.jpg').cqcode)

@sv.on_keyword(('xcw', '镜华'))
async def chat_xcw(bot, ctx):
    if random.random() < 0.2:
        await bot.send(ctx, R.img('xcw.jpg').cqcode)

@sv.on_keyword(('暴击'))
async def chat_baoji(bot, ctx):
    if random.random() < 0.1:
        await bot.send(ctx, R.img('暴击.jpg').cqcode)

@sv.on_keyword(('欧'))
async def chat_ouhuang(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('欧.jpg').cqcode)

@sv.on_keyword(('赞'))
async def chat_dianzan(bot, ctx):
    if random.random() < 0.4:
        await bot.send(ctx, R.img('赞.jpg').cqcode)

@sv.on_keyword(('钻'))
async def chat_zhuan(bot, ctx):
    if random.random() < 0.2:
        await bot.send(ctx, R.img('钻.gif').cqcode)

@sv.on_keyword(('吃饭','盒饭'))
async def chat_dianzan(bot, ctx):
    if random.random() < 0.4:
        await bot.send(ctx, R.img('饭.jpg').cqcode)

@sv.on_keyword(('xp','XP'))
async def chat_xp(bot, ctx):
    if random.random() < 0.4:
        await bot.send(ctx, R.img('xp.jpg').cqcode)

@sv.on_keyword(('三刀'))
async def chat_sandao(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('三刀.jpg').cqcode)

@sv.on_keyword(('不抽'))
async def chat_buchou(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('不抽.jpg').cqcode)

@sv.on_keyword(('咕噜灵波','gglb','咕噜灵啵'))
async def chat_gglb(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('咕噜灵波.jpg').cqcode)

@sv.on_keyword(('吃瓜'))
async def chat_chigua(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('吃瓜.jpg').cqcode)

@sv.on_keyword(('爬'))
async def chat_pa(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('爬.jpg').cqcode)

@sv.on_keyword(('叹气','哎'))
async def chat_tanqi(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('叹气.jpg').cqcode)

@sv.on_keyword(('退坑','弃坑'))
async def chat_tuikeng(bot, ctx):
    if random.random() < 0.2:
        await bot.send(ctx, R.img('退坑.jpg').cqcode)
# ============================================ #
@sv.on_keyword(('暴击弓', '玲奈'))
async def chat_lingnai(bot, ctx):
    if random.random() < 0.2:
        await bot.send(ctx, R.img('暴击弓.jpg').cqcode)

@sv.on_keyword(('爽弓', '爱丽丝弓'))
async def chat_sg(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('爽弓.GIF').cqcode)

@sv.on_keyword(('裁缝'))
async def chat_caifeng(bot, ctx):
    if random.random() < 0.03:
        await bot.send(ctx, R.img('裁缝.jpg').cqcode)
# ============================================ #
@sv.on_keyword(('伤害优衣的家伙', '迫害优衣'))
async def chat_shanghaiue(bot, ctx):
    if random.random() < 0.7:
        await bot.send(ctx, R.img('迫害.jpg').cqcode)

@sv.on_keyword(('睡了'))
async def chat_shuile(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('睡了.jpg').cqcode)

@sv.on_keyword(('肝'))
async def chat_gan(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('肝.jpg').cqcode)

@sv.on_keyword(('氪'))
async def chat_kejin(bot, ctx):
    if random.random() < 0.2:
        await bot.send(ctx, R.img('氪金.jpg').cqcode)

@sv.on_keyword(('炼铜'))
async def chat_liantong(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('炼铜.jpg').cqcode)

@sv.on_keyword(('摸了'))
async def chat_mole(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('会战摸了.jpg').cqcode)

@sv.on_keyword(('就这', '阿这', '啊这'))
async def chat_jiuzhe(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('就这.jpg').cqcode)

@sv.on_keyword('举高高')
async def chat_jugao(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('举高高.jpg').cqcode)
        
@sv.on_keyword(('快了'))
async def chat_kuaile(bot, ctx):
    if random.random() < 0.5:
        await bot.send(ctx, R.img('快了.jpg').cqcode)

@sv.on_keyword('娱乐')
async def chat_yule(bot, ctx):
    if random.random() < 0.3:
        await bot.send(ctx, R.img('沙雕1.gif').cqcode)

@sv.on_keyword(('了', '哦', '哈', '的', '嘿'))
async def chat_touting(bot, ctx):
    if random.random() < 0.01:
        await bot.send(ctx, R.img('偷听.jpg').cqcode)

@sv.on_keyword(('嗯', '恩', '乐', '美', '学'))
async def chat_ueue(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('ueue.jpg').cqcode)
        
@sv.on_keyword(('？', '?'))
async def chat_wenhao(bot, ctx):
    if random.random() < 0.1:
        await bot.send(ctx, R.img('问号.jpg').cqcode)

@sv.on_keyword(('。', '，'))
async def chat_uegonglian(bot, ctx):
    if random.random() < 0.05:
        await bot.send(ctx, R.img('ue脸红.jpg').cqcode)


