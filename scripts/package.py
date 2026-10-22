from pathlib import Path
from bs4 import BeautifulSoup
from verify import verify
import base64
import json
import mimetypes
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def standalone():
    soup=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
    for link in soup.select('link[rel=stylesheet]'):
        style=soup.new_tag('style');style.string=(ROOT/link['href']).read_text();link.replace_with(style)
    for old in soup.select('script[src]'):
        script=soup.new_tag('script');script.string=(ROOT/old['src']).read_text();old.decompose();soup.body.append(script)
    for img in soup.select('img[src]'):
        if img['src'].startswith('data:'):continue
        file=ROOT/img['src'];mime=mimetypes.guess_type(file.name)[0]
        img['src']='data:'+mime+';base64,'+base64.b64encode(file.read_bytes()).decode()
    return str(soup)

def main():
    target=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'build'
    target.mkdir(parents=True,exist_ok=True)
    report=verify()
    output=target/'红楼梦前十回.html';output.write_text(standalone())
    assert verify(output)['all_exactly_equal']
    (target/'前十回文字校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(target/'红楼梦前十回-完整源码.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob('*'):
            rel=p.relative_to(ROOT)
            if p.is_file() and not any(s in {'.git','__pycache__','build'} for s in rel.parts):z.write(p,Path('honglou-ebook')/rel)
    print(output,output.stat().st_size)

if __name__=='__main__':main()
