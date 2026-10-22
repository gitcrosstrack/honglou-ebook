"""Import frozen Wikisource HTML without rewriting the literary text."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def extract(path):
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    content = soup.select_one('.mw-parser-output')
    header = content.select_one('div.center')
    for ref in header.select('sup.reference'):
        ref.decompose()
    title = header.get_text().strip()
    revision = parse_qs(urlparse(soup.select_one('#t-permalink a')['href']).query)['oldid'][0]
    blocks, started = [], False
    for node in content.children:
        if not getattr(node, 'name', None):
            continue
        if node is header:
            started = True
            continue
        if not started:
            continue
        if node.name == 'hr' or 'mw-heading' in node.get('class', []):
            break
        for ref in node.select('sup.reference'):
            ref.decompose()
        if node.name == 'figure':
            img = node.select_one('img')
            blocks.append({'type':'source-image', 'alt':img.get('alt', ''), 'url':'https:'+img['src'].split('?')[0], 'width':int(img['width']), 'height':int(img['height'])})
            continue
        if node.name not in ('p', 'div'):
            raise ValueError(f'Unexpected source element: {path}: {node.name}')
        text = node.get_text().strip()
        if text:
            kind = 'poem' if 'poem' in node.get('class', []) else 'center' if 'center' in node.get('class', []) else 'prose'
            blocks.append({'type':kind, 'text':text})
    notes = [li.get_text(' ',strip=True).replace('↑ ', '', 1) for li in content.select('ol.references > li')]
    return title, revision, blocks, notes

def main():
    chapters=[]
    for i in range(1,11):
        path=ROOT/'sources'/f'chapter-{i:02d}.html'
        title,rev,blocks,notes=extract(path)
        for index,b in enumerate(blocks):
            if b['type']=='source-image':
                asset=f'assets/source-ch{i:02d}-{index:02d}.jpg'
                dest=ROOT/asset
                if not dest.exists():
                    subprocess.run(['curl','-fsSL','--retry','2','-A','Mozilla/5.0',b['url'],'-o',str(dest)],check=True)
                b['src']=asset
                b['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
        plain='\n\n'.join(b['text'] for b in blocks if 'text' in b)
        ch={'id':i,'title':title,'revision':rev,'source':f'https://zh.wikisource.org/zh-hans/紅樓夢/第{i:03d}回','frozenSource':f'sources/chapter-{i:02d}.html','downloaded':'2026-10-22','blocks':blocks,'notes':notes,'characters':sum(len(b.get('text','')) for b in blocks),'text_sha256':hashlib.sha256(plain.encode()).hexdigest(),'html_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        chapters.append(ch)
        print(i,title,'blocks',len(blocks),'chars',ch['characters'],'revision',rev)
    (ROOT/'data'/'chapters.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
