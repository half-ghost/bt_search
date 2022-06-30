help_text = f'''[搜磁力numtag]:num为指定的引擎，目前有3个，tag为搜索关键词
[聚合搜索tag]:将所有引擎的搜索结果合并起来，tag为搜索关键词
'''

from bs4 import BeautifulSoup as bs
import asyncio
from hoshino import Service,aiorequests
import math
import random
import json

ciliwang = {
    "磁力猫":"https://clm182.xyz/",
    "搜磁力":"https://soucili.info",
    "种子搜":"https://m.zhongziso19.xyz/",
    "磁力蜘蛛":"http://www.eclzz.win"
}

async def clm_beiyong():
    reps = await aiorequests.get("https://xn--tfrs17es0d.com/", timeout = 6)
    text = await reps.text
    soup = bs(text, "lxml")
    url_list = []
    for i in soup.findAll(name = "a", target = "_blank"):
        url = i.get("href")
        url_list.append(url)
    return url_list

async def clm_crawler(tag):
    url = ciliwang.get("磁力猫")
    try:
        geturl = await aiorequests.get(url+f"search-{tag}-0-0-1.html", timeout = 6)
    except:
        url_list = await clm_beiyong()
        for url in url_list:
            try:
                geturl = await aiorequests.get(url+f"/search-{tag}-0-0-1.html", timeout = 6)
                if geturl.status_code == 200:
                    break
            except:
                if url_list.index(url) == len(url_list)-1:
                    return []
                else:
                    continue
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    box_soup = soup.findAll(name = "div", class_ = "ssbox")
    for i in box_soup:
        title = i.find(name = "div", class_ = "title").a
        sbar = i.find(name = "div", class_ = "sbar")
        title_text = title.text
        title_list.append(title_text.replace(tag, f"『{tag}』"))
        sbar_span = sbar.findAll(name = "span")
        info = ""
        for span in sbar_span:
            if span.text == "[磁力链接]":
                magnet = span.a.get("href")
                magnet_list.append(magnet)
                continue
            info += span.text + " "
        info_list.append(info)
    if len(title_list) == 0:
        return []
    else:
        return title_list, magnet_list, info_list, url

async def zzs_crawler(tag):
    url = ciliwang.get("种子搜")
    try:
        geturl = await aiorequests.get(url+f"list/{tag}/1", timeout = 6)
    except:
        return []
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    table_list = soup.findAll(name = "ul", class_ = "list-group")
    for table in table_list:
        a = table.find(name = "a", class_ = "text-success")
        title = a.text
        title_list.append(title.replace(tag, f"『{tag}』"))
        magnet = a.get("href").replace("/info-", "magnet:?xt=urn:btih:")
        magnet_list.append(magnet)
        info_dl = table.find(name = "dl", class_ = "list-code").contents
        info_text = ""
        for content in info_dl:
            if content == "\n" or "text-type" in content.get("class", ""):
                continue
            info_text += content.text + " "
        info_list.append(info_text)
    if len(title_list) == 0:
        return []
    else:
        return title_list, magnet_list, info_list, url

async def clzz_crawler(tag):
    url = ciliwang.get("磁力蜘蛛")
    try:
        geturl = await aiorequests.get(url+f"/s/{tag}.html", timeout = 6)
    except:
        return []
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    item_list = soup.findAll(name = "div", class_ = "search-item")
    for item in item_list:
        if item.text == "没有找到记录！":
            return title_list
        itemtitle = item.find(name = "div", class_ = "item-title")
        itembar = item.find(name = "div", class_ = "item-bar")
        title = itemtitle.a.text
        title_list.append(title.replace(tag, f"『{tag}』"))
        magnet = itemtitle.a.get("href").replace("/detail/", "magnet:?xt=urn:btih:").replace(".html", "")
        magnet_list.append(magnet)
        bar_list = itembar.findAll(name = "span")
        info = ""
        for span in bar_list:
            if span.get("class"):
                continue
            info += span.text.strip() + " "
        info_list.append(info.replace("\n", "").replace("\t", ""))
    if len(title_list) == 0:
        return []
    else:
        return title_list, magnet_list, info_list, url

async def soucili(tag):
    soucilihead = {
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'X-Requested-With': "XMLHttpRequest",
        'Referer': 'https://soucili.info/'
    }
    def id():
        a = hex(math.floor((1 + random.random()) * 65536))[3:]
        return a
    def calculate_size(size):
        def strofsize(integer, remainder, level):
            if integer >= 1024:
                remainder = integer % 1024
                integer //= 1024
                level += 1
                return strofsize(integer, remainder, level)
            else:
                return integer, remainder, level
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        integer, remainder, level = strofsize(size, 0, 0)
        if level+1 > len(units):
            level = -1
        return ( '{}.{:>03d} {}'.format(integer, remainder, units[level]) )
    device_id = f"{id()}{id()}-{id()}-{id()}-{id()}-{id()}{id()}{id()}"
    url = ciliwang.get("搜磁力")
    geturl = await aiorequests.get(f"{url}/request/?request_type=esearch&keywords={tag}&device_id={device_id}&page=0", headers=soucilihead)
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    resp = await geturl.text
    json_page = json.loads(resp)
    title_list, magnet_list, info_list = [],[],[]
    if json_page['videos'] == "":
        return []
    for i in json_page['videos']:
        title_list.append(i['file_name'].replace(tag, f"『{tag}』"))
        magnet_list.append("magnet:?xt=urn:btih:" + i['moc'])
        info_list.append(f"大小:{calculate_size(i['file_size'])} 添加时间:{i['create_time']} 热度:{i['hot']}")

    return title_list, magnet_list, info_list, url

def mes_creater(data):
    title_list, magnet_list, info_list, url = data
    mes_list = []
    mes_list.append({
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"以下搜索结果来自于{url}"
                        }
                })
    for i in range(len(title_list)):
        data = {
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"{title_list[i]}\n{magnet_list[i]}\n{info_list[i]}"
                        }
                }
        mes_list.append(data)
    return mes_list

async def engine_search(tag, engine=None, All=False):
    if All:
        result = []
        result_list = await asyncio.gather(clm_crawler(tag),zzs_crawler(tag),clzz_crawler(tag),soucili(tag))
        for i in result_list:
            if len(i) == 0 or i == "bad":
                continue
            result += mes_creater(i)
        return result

    if engine == "1":
        result = await clm_crawler(tag)
    elif engine == "2":
        result = await zzs_crawler(tag)
    elif engine == "3":
        result = await clzz_crawler(tag)
    elif engine == "4":
        result = await soucili(tag)
    if result == "bad":
        return "该引擎访问失败，请更换引擎重试"
    if len(result) == 0:
        return "无搜索结果，请更换关键词重试"

    return mes_creater(result)

sv = Service("磁力搜bot", help_ = help_text)

@sv.on_prefix("聚合搜索")
async def gather_search(bot, ev):
    tag = ev.raw_message.replace("聚合搜索", "").strip()
    await bot.send(ev, "聚合搜索需要的时间较长，请耐心等待")
    result = await engine_search(tag, All=True)
    if isinstance(result, list):
        try:
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=result)
        except Exception as e:
            if "retcode=100" in str(e):
                await bot.send(ev, "消息可能被风控，请使用单引擎搜索指令")
    else:
        await bot.send(ev, result)
    
@sv.on_prefix("搜磁力")
async def single_search(bot, ev):
    mes = ev.raw_message.replace("搜磁力", "")
    engine = mes[:1]
    if engine not in "1234":
        await bot.send(ev, "请指定搜索引擎(目前有4个引擎)")
        return
    tag = mes[1:].strip()
    await bot.send(ev, "请等待搜索结果")
    result = await engine_search(tag, engine)
    if isinstance(result, list):
        try:
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=result)
        except Exception as e:
            if "retcode=100" in str(e):
                await bot.send(ev, "消息可能被风控，请尝试使用指令搜索其他引擎")
    else:
        await bot.send(ev, result)

@sv.on_fullmatch("磁力帮助")
async def help(bot, ev):
    await bot.send(ev, help_text)
