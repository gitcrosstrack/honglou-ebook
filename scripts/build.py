"""Build a static reader and a self-contained, offline HTML edition."""
from pathlib import Path
from bs4 import BeautifulSoup
import base64
import html
import json
import re

ROOT=Path(__file__).resolve().parents[1]
E=html.escape

def part(soup, markup):
    return BeautifulSoup(markup,'html.parser')

def navigation(chapters):
    out=[]
    for ch in chapters:
        fields=ch['title'].split('　')
        out.append(f'<button type="button" data-chapter="{ch["id"]}"><em>{ch["id"]:02d}</em><span>{E(fields[0])}<small>{E(fields[1])}</small></span></button>')
    return ''.join(out)

def figure(ill,ch):
    i=ill['before']
    context=ch['blocks'][i]['text'][:65]
    ill['source_excerpt']=context
    return f'''<figure class="illustration" data-scene-chapter="{ch['id']}" data-scene-block="{i}"><img src="{ill['src']}" alt="{E(ill['alt'])}" width="1536" height="1024" loading="lazy"><figcaption><span>{E(ill['title'])}</span><span class="scene-info">{E(ill['scene'])}</span><button class="scene-link sans" data-jump="ch{ch['id']}-p{i}">对应原文 ↗</button><span class="scene-context sans">图意据本回原文：{E(context)}…<br>AI 绘制的情节插画</span></figcaption></figure>'''

def chapter_html(ch,illustrations):
    n=ch['id'];fields=ch['title'].split('　');label=fields[0]
    body=[]
    for i,b in enumerate(ch['blocks']):
        for ill in illustrations:
            if ill['chapter']==n and ill['before']==i:body.append(figure(ill,ch))
        if b['type']=='source-image':
            body.append(f'<figure class="source-plate"><img src="{b["src"]}" width="{b["width"]}" height="{b["height"]}" alt="{E(b["alt"])}" loading="lazy"><figcaption class="sans">底本原图 · 保留原样</figcaption></figure>')
        else:
            tag='p' if b['type']=='prose' else 'div'
            long=' long' if b['type']=='poem' and len(b['text'])>120 else ''
            body.append(f'<{tag} id="ch{n}-p{i}" class="original {b["type"]}{long}" data-index="{i}">{E(b["text"])}</{tag}>')
    noteitems=''.join(f'<li>{E(note)}</li>' for note in ch['notes'])
    notes=f'<p>底本注释：</p><ol>{noteitems}</ol>' if noteitems else ''
    source=f'''<details class="source sans" id="source-{n}"><summary>本回底本与文字校验</summary><div class="edition"><p>维基文库《红楼梦》汇校本 · 简体显示 · {label}<br>固定修订号 {ch['revision']} · 采集日期 2026-10-22</p><p>正文及诗词逐段保留所选底本的字词、标点和异文，未作改写或润色。仅调整显示排版，底本注释号移至本栏。不同版本可能存在异文；回目亦以所选底本为准。第一回底本收录的回前文字与诗保留在篇首，其性质见底本注释。</p><p>本回共 {len([b for b in ch['blocks'] if 'text' in b])} 个文字段落，{ch['characters']:,} 个字符（含标点与段内换行）。第八回底本的四幅宝玉、金锁图式原样保留。新绘插画、图题和导航均独立呈现，不属于小说正文。</p><p><a href="{E(ch['source'])}" target="_blank" rel="noopener noreferrer">查看来源 ↗</a>　<a href="https://zh.wikisource.org/w/index.php?title=紅樓夢/第{n:03d}回&amp;oldid={ch['revision']}&amp;variant=zh-hans" target="_blank" rel="noopener noreferrer">固定版本 ↗</a></p></div>{notes}<p class="proof">文字 SHA-256：{ch['text_sha256']}</p></details>'''
    return f'''<article class="chapter-page" id="chapter-{n}" data-chapter-id="{n}" data-label="{label}" data-characters="{ch['characters']}" aria-label="红楼梦{label}正文" {'hidden' if n>1 else ''}><header class="chapter-heading"><p class="chapter-number">{label}</p><h2 tabindex="-1">{E(fields[1])}<br>{E(fields[2])}</h2><span class="ornament" aria-hidden="true"></span></header><div class="original-body">{''.join(body)}</div><div class="end-mark"><span>{label}终</span></div><nav class="chapter-pager sans" aria-label="{label}章节切换"><button data-action="prev" {'disabled' if n==1 else ''}>← 上一回</button><span class="pager-count">{n:02d} / 10</span><button data-action="next" {'disabled' if n==10 else ''}>下一回 →</button></nav>{source}</article>'''

def main():
    chapters=json.loads((ROOT/'data/chapters.json').read_text())
    illustrations=json.loads((ROOT/'data/illustrations.json').read_text())
    soup=BeautifulSoup((ROOT/'src/shell.html').read_text(),'html.parser')
    soup.title.string='红楼梦 · 前十回 | 一卷红楼'
    soup.select_one('meta[name=description]')['content']='红楼梦前十回合卷。完整底本逐段校验，情节对应古典插画，支持 Web/H5、章节切换、夜读、书签与续读。'
    soup.style.decompose()
    for script in soup.select('script'):script.decompose()
    link=soup.new_tag('link',rel='stylesheet',href='styles.css');soup.head.append(link)
    soup.select_one('.hero-meta').string='中国古典文学 · 前十回合卷'
    start=soup.select_one('.primary');start.name='button';del start['href'];start['data-action']='start';start.clear();start.append('展卷 · 第一回');arrow=soup.new_tag('span');arrow['aria-hidden']='true';arrow.string='↗';start.append(arrow)
    brand=soup.select_one('.brand');brand.name='button';del brand['href'];brand['data-action']='top'
    skip=soup.select_one('.skip');skip.name='button';del skip['href'];skip['data-action']='start'
    total=sum(ch['characters'] for ch in chapters)
    soup.select_one('.chapter-band').replace_with(part(soup,f'<div class="chapter-band sans"><div><strong>第一至十回 · 完整原文</strong><span class="book-total">{total:,} 字</span><span class="desktop-stat">十二幅情节绘图 · 四幅底本图式</span></div><button class="source-button" data-action="source">本回底本说明 ↗</button></div>'))
    nav=navigation(chapters)
    soup.select_one('.rail').replace_with(part(soup,f'<aside class="rail"><p class="rail-title">卷一目录</p><nav class="book-toc" aria-label="章节目录">{nav}</nav><div class="rail-bottom sans"><p><span class="current-chapter">第一回</span> · 位置 <strong class="progress">0</strong> %</p><button data-action="saved">我的书签与续读 ↗</button></div></aside>'))
    options=''.join(f'<option value="{ch["id"]}">{E(ch["title"])}</option>' for ch in chapters)
    strip=f'<div class="volume-strip sans"><label for="current-select">正在阅读</label><span id="current-stat">本回 7,888 字 · 共十回</span><select id="current-select" aria-label="选择章节">{options}</select></div>'
    soup.select_one('#chapter').replace_with(part(soup,'<div class="chapter-region">'+strip+''.join(chapter_html(ch,illustrations) for ch in chapters)+'</div>'))
    soup.select_one('.footer').replace_with(part(soup,'<footer class="footer"><span>一卷红楼 · 在字里行间，重逢旧梦。</span><span>第一至十回合卷 · 曹雪芹</span></footer>'))
    soup.select_one('.reader-bar').replace_with(part(soup,'<nav class="reader-bar sans" aria-label="快捷阅读工具"><span class="bar-label"><span class="current-chapter">第一回</span> <span class="progress">0</span>%</span><button data-action="prev" aria-label="上一回" disabled>←</button><button data-action="toc">目录</button><button data-action="settings">字号</button><button data-action="bookmark" aria-pressed="false">书签</button><button data-action="next" aria-label="下一回">→</button></nav>'))
    soup.select_one('#toc-dialog').replace_with(part(soup,f'<dialog id="toc-dialog" class="toc-dialog" aria-labelledby="toc-title"><div class="dialog-head"><h3 id="toc-title">卷 一 · 目 录</h3><button class="close" data-close aria-label="关闭目录">×</button></div><p class="toc-hint sans">第一至十回 · 选择回目即可展卷</p><nav class="book-toc" aria-label="全部章节">{nav}</nav><section class="bookmarks sans"><h4>我的书签</h4><p id="bookmark-empty">尚无书签，阅读时点击“书签”保存当前位置。</p><div id="saved-list"></div></section></dialog>'))
    for a in soup.select('a[href^="#"]'):
        a.name='button';del a['href'];a['data-action']='top'
    script=soup.new_tag('script',src='reader.js');script['defer']='';soup.head.append(script)
    noscript=soup.new_tag('noscript');noscript.append(part(soup,'<style>.chapter-page[hidden]{display:block!important}.reader-bar,.rail,.volume-strip{display:none!important}</style>'));soup.head.append(noscript)
    css=(ROOT/'src/styles.css').read_text()+'\n'+(ROOT/'src/volume.css').read_text()
    (ROOT/'styles.css').write_text(css)
    (ROOT/'reader.js').write_text((ROOT/'src/reader.js').read_text())
    (ROOT/'index.html').write_text(str(soup))
    (ROOT/'.nojekyll').touch()
    (ROOT/'data/illustrations.json').write_text(json.dumps(illustrations,ensure_ascii=False,indent=2))
    print(f'Built {len(chapters)} chapters / {total:,} characters / {len(illustrations)+1} generated paintings')

if __name__=='__main__':main()
