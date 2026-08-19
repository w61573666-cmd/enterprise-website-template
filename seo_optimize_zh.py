# -*- coding: utf-8 -*-
"""
恒生石材中文版 40 个页面 SEO 关键词全面优化脚本
- 在保留原有内容/结构/验证码/JSON-LD/canonical/hreflang/CSS版本号的前提下
- 将简化的中文关键词(云石/麻石/平方呎/直呎)自然分布到 title/H1-H3/meta description/正文/图片alt/meta keywords
- 每页叠加分配的关键词，并保证全部关键词至少出现于一个页面
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# 每个页面: 相对路径 -> (name_cn 用于 title/正文展示, kws 该页分配的关键词列表(简化形式))
PAGES = {
    "index.html": ("恒生石材科技", ["香港云石公司","香港云石供应商","香港云石厂","天然云石","天然大理石","云石大板香港","云石入口商香港","香港本地云石工场","云石工程香港"]),
    "about.html": ("关于恒生石材", ["香港云石公司","香港大理石公司","香港麻石公司","进口云石香港","云石入口商香港","香港大理石供应商"]),
    "contact.html": ("联络恒生石材", ["香港云石报价","云石几钱一呎","云石每平方呎价钱","云石直呎报价","香港边度买云石","云石安装收费"]),
    "faq.html": ("常见问题", ["云石几钱一呎","云石每平方呎价钱","云石翻新费用","云石安装收费","厨房云石台面价钱","云石楼梯造价香港"]),
    "news.html": ("石材新闻资讯", ["香港云石公司","云石工程香港"]),
    "privacy.html": ("私隐政策", ["香港云石公司"]),
    "sample-request.html": ("索取云石样板", ["云石大板香港","云石薄板","香港本地云石工场","样板房云石"]),
    "products.html": ("云石产品中心", ["云石大板香港","云石薄板","云石厚板","云石马赛克","复合云石","透光云石","花岗岩石板","石英石","水磨石","洞石","玉石云石","天然云石供应","人造云石","绿色云石","红色云石"]),
    "products/white-marble.html": ("白色云石系列", ["白色云石","卡拉拉白云石","爵士白云石","天然云石","意大利云石香港","希腊云石香港"]),
    "products/beige-marble.html": ("米黄云石系列", ["米黄云石","罗马米黄云石","莎安娜米黄云石","天然大理石","浅啡网云石","威尼斯棕云石","啡色云石"]),
    "products/grey-marble.html": ("灰色大理石系列", ["灰色大理石","灰色云石","天然云石"]),
    "products/black-marble.html": ("黑色云石系列", ["黑色云石","黑金花云石","天然麻石","深啡网云石"]),
    "products/granite-collection.html": ("花岗岩石板系列", ["花岗岩石板","香港麻石公司","巴西麻石香港","天然麻石"]),
    "products/luxury-stone.html": ("玉石云石奢石系列", ["玉石云石","透光云石","复合云石"]),
    "products/travertine-sandstone.html": ("洞石水磨石系列", ["洞石","水磨石","石英石"]),
    "products/custom-craft.html": ("云石定制加工", ["云石台面","云石洗手台","云石壁炉","云石餐台","云石茶几","云石门套","浴室云石台面","云石窗台","云石门槛石"]),
    "products/project-stone.html": ("工程云石系列", ["云石薄板","云石厚板","工程云石"]),
    "products/new-arrivals.html": ("最新进口云石", ["进口云石香港","意大利云石香港","西班牙云石香港","土耳其云石香港"]),
    "projects.html": ("云石工程案例", ["云石工程香港","麻石工程香港","会所云石工程","酒店云石墙身","商场云石地台","云石地台","云石楼梯"]),
    "projects/hotel.html": ("酒店云石工程", ["酒店云石供应商","酒店云石墙身","云石工程香港"]),
    "projects/commercial.html": ("商业空间云石工程", ["写字楼云石装修","商场云石地台"]),
    "projects/residential.html": ("私人住宅云石", ["私人住宅云石","豪宅云石供应商"]),
    "projects/villa.html": ("别墅云石工程", ["别墅云石工程","豪宅云石供应商","云石楼梯踏步","云石玄关地台"]),
    "projects/resort.html": ("度假村云石工程", ["酒店云石供应商","泳池麻石铺砌","露台麻石","花园麻石","样板房云石"]),
    "projects/mall.html": ("商场云石地台工程", ["商场云石地台"]),
    "projects/bank.html": ("银行云石工程", ["写字楼云石装修"]),
    "projects/airport.html": ("机场云石工程", ["云石工程香港"]),
    "projects/metro.html": ("地铁麻石工程", ["麻石工程香港","户外麻石地台"]),
    "projects/stadium.html": ("体育场麻石工程", ["麻石工程香港"]),
    "projects/museum.html": ("博物馆云石工程", ["云石墙身"]),
    "projects/medical.html": ("医疗机构云石工程", ["云石工程香港"]),
    "projects/education.html": ("教育机构云石工程", ["云石工程香港"]),
    "projects/government.html": ("政府云石工程", ["云石工程香港"]),
    "projects/convention.html": ("会展中心云石工程", ["云石工程香港"]),
    "projects/office.html": ("写字楼云石装修", ["写字楼云石装修"]),
    "solutions.html": ("云石解决方案", ["云石加工","云石安装","云石铺砌","云石翻新","云石打磨抛光","云石补胶","云石晶面处理","云石防污处理","云石维修","旧云石翻新","云石拆除更换"]),
    "solutions/architect.html": ("建筑师云石方案", ["云石上门度尺","云石大板香港"]),
    "solutions/contractor.html": ("承建商云石方案", ["云石安装","云石铺砌","云石切割","云石磨边","云石倒角","云石钻孔","云石开料"]),
    "solutions/developer.html": ("发展商云石方案", ["云石工程香港","云石工程报价单","豪宅云石造价"]),
    "solutions/trader.html": ("贸易商云石方案", ["云石入口商香港","香港云石批发商","云石大板香港"]),
}

# 通用正文段落(第二段落)：自然融入工序/报价类关键词，保证全部页面覆盖核心词
P2 = ("无论" + "云石台面" + "、" + "云石地台" + "抑或" + "云石墙身" + "工程，我们均可按图纸" + "云石上门度尺" +
      "，提供" + "云石工程报价单" + "与" + "云石每平方呎价钱" + "明细；并由专业团队负责" + "云石安装" + "、" +
      "云石铺砌" + "、" + "云石翻新" + "、" + "云石打磨抛光" + "、" + "云石补胶" + "、" + "云石晶面处理" +
      "及" + "云石防污处理" + "，" + "旧云石翻新" + "与" + "云石拆除更换" + "亦可代办。欢迎查询" +
      "香港云石报价" + "、" + "云石几钱一呎" + "、" + "云石直呎报价" + "及" + "云石安装收费" + "，" +
      "香港边度买云石" + "均可联络我们索取" + "云石报价" + "。")


def gen_title(name_cn, kws):
    title_kw = "・".join(kws[:3])
    return f"{name_cn}｜{title_kw} | HENGSHENG MARBLE S&T"


def gen_description(name_cn, kws):
    parts = [k for k in kws[:3] if k]
    kwstr = "、".join(parts) if parts else "天然云石"
    return (f"{name_cn} — 恒生石材作为" + "香港云石公司" + "与" + "香港云石供应商" +
            f"，专营{kwstr}等天然云石与" + "云石工程香港" +
            "服务，均由" + "香港本地云石工场" + "严选直供，欢迎索取" + "香港云石报价" +
            "及" + "云石每平方呎价钱" + "。")


def gen_body(name_cn, kws):
    chunks = [kws[i:i + 4] for i in range(0, len(kws), 4)]
    verbs = ["专营", "提供", "涵盖", "配套", "支援", "供应"]
    parts = []
    for i, ch in enumerate(chunks):
        v = verbs[i % len(verbs)]
        parts.append(f"{v}{'、'.join(ch)}等")
    mid = "，".join(parts)
    p1 = (f"恒生石材科技有限公司是" + "香港云石公司" + "与" + "香港云石供应商" + f"，{mid}全系列天然云石及" +
          "云石工程香港" + "服务，均由" + "香港本地云石工场" + "严选直供。")
    h2 = f"{kws[0]}・{(kws[1] if len(kws) > 1 else name_cn)} 专业供应"
    h3 = f"{(kws[2] if len(kws) > 2 else '云石工程与售后')} 应用场景"
    block = (
        '<section class="seo-keywords-block">\n'
        f'  <h2>{h2}</h2>\n'
        f'  <p>{p1}</p>\n'
        f'  <h3>{h3}</h3>\n'
        f'  <p>{P2}</p>\n'
        '</section>\n'
    )
    return block


def gen_alts(name_cn, kws, n):
    lead = kws[0] if kws else "云石"
    pool = [
        f"{lead}大板详情 — {name_cn}天然云石纹理特写",
        f"{name_cn}铺砌实景 — {lead}应用展示",
        f"{lead}样板展示 — {name_cn}表面工艺特写",
        f"{name_cn}工程实例 — {lead}效果详解",
    ]
    return [pool[i % len(pool)] for i in range(n)]


def replace_title(text, new_title):
    matches = list(re.finditer(r'<title>(.*?)</title>', text, re.S))
    best = None
    for m in matches:
        s = m.group(1).strip()
        if s and (best is None or len(s) > len(best.group(1).strip())):
            best = m
    if best is None:
        return text
    return text[:best.start()] + f'<title>{new_title}</title>' + text[best.end():]


def replace_description(text, new_desc):
    pat = re.compile(r'<meta\b[^>]*\bname="description"[^>]*>+', re.S)
    m = pat.search(text)
    if not m:
        return text
    new_tag = f'<meta name="description" content="{new_desc}"/>'
    return text[:m.start()] + new_tag + text[m.end():]


def update_keywords(text, kws):
    pat = re.compile(r'<meta\b[^>]*\bname="keywords"[^>]*>+', re.S)
    m = pat.search(text)
    if m:
        tag = m.group(0)
        cm = re.search(r'content="([^"]*)"', tag)
        old = cm.group(1) if cm else ""
        combined = [x for x in old.split(',') if x.strip()] if old else []
        for k in kws:
            if k not in combined:
                combined.append(k)
        new_content = ','.join(combined)
        new_tag = re.sub(r'content="[^"]*"', f'content="{new_content}"', tag)
        return text[:m.start()] + new_tag + text[m.end():]
    else:
        new_tag = f'<meta name="keywords" content="{",".join(kws)}"/>'
        dm = re.search(r'<meta\b[^>]*\bname="description"[^>]*>+', text)
        if dm:
            return text[:dm.end()] + '\n  ' + new_tag + text[dm.end():]
        hm = re.search(r'<head[^>]*>', text)
        if hm:
            return text[:hm.end()] + '\n  ' + new_tag + text[hm.end():]
        return text


def update_h1(text, kws):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S)
    if not m:
        return text
    h1 = m.group(1)
    if any(k in h1 for k in kws):
        return text
    new_h1 = f"{kws[0]}｜{h1.strip()}"
    return text[:m.start()] + m.group(0)[:m.group(0).index('>') + 1] + new_h1 + text[m.end() - len('</h1>'):]


def update_alts(text, name_cn, kws):
    n = len(re.findall(r'alt="Product detail"', text, re.I))
    if n == 0:
        return text
    alts = gen_alts(name_cn, kws, n)
    idx = [0]

    def repl(mm):
        a = alts[idx[0] % len(alts)]
        idx[0] += 1
        return f'alt="{a}"'

    return re.sub(r'alt="Product detail"', repl, text, flags=re.I)


def insert_block(text, block):
    marker = '<footer class="footer">'
    idx = text.find(marker)
    if idx == -1:
        idx = text.find('</body>')
    if idx == -1:
        return text + block
    return text[:idx] + block + text[idx:]


def div_balanced(text):
    opens = len(re.findall(r'<div\b', text))
    closes = len(re.findall(r'</div>', text))
    return opens == closes, opens, closes


def process(path, name_cn, kws):
    full = os.path.join(ROOT, path)
    with open(full, 'r', encoding='utf-8') as f:
        text = f.read()
    if 'seo-keywords-block' in text:
        print(f"SKIP (already done): {path}")
        return True

    block = gen_body(name_cn, kws)
    text = replace_title(text, gen_title(name_cn, kws))
    text = replace_description(text, gen_description(name_cn, kws))
    text = update_keywords(text, kws)
    text = update_h1(text, kws)
    text = update_alts(text, name_cn, kws)
    text = insert_block(text, block)

    ok, o, c = div_balanced(text)
    if not ok:
        print(f"WARN div imbalance {path}: open={o} close={c}")
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"OK {path} (div {'balanced' if ok else 'IMBALANCED'})")
    return ok


def main():
    all_ok = True
    for path, (name_cn, kws) in PAGES.items():
        if not process(path, name_cn, kws):
            all_ok = False
    print("\n=== DONE ===" if all_ok else "\n=== DONE WITH WARNINGS ===")


if __name__ == '__main__':
    main()
