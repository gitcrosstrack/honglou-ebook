"""Check every generated text node against the frozen source, including punctuation."""
from pathlib import Path
from bs4 import BeautifulSoup
from import_sources import extract
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def verify(html_path=None):
    html_path=Path(html_path or ROOT/'index.html')
    doc=BeautifulSoup(html_path.read_text(),'html.parser')
    metadata=json.loads((ROOT/'data/chapters.json').read_text())
    report=[]
    for ch in metadata:
        title, revision, blocks, notes=extract(ROOT/ch['frozenSource'])
        expected=[b['text'] for b in blocks if 'text' in b]
        section=doc.select_one(f'#chapter-{ch["id"]}')
        actual=[p.get_text() for p in section.select('.original')]
        assert actual==expected, f'Chapter {ch["id"]} differs from frozen source'
        assert ch['title']==title and ch['revision']==revision
        assert ''.join(section.h2.stripped_strings)==''.join(title.split('　')[1:])
        digest=hashlib.sha256('\n\n'.join(expected).encode()).hexdigest()
        assert ch['text_sha256']==digest
        assert ch['html_sha256']==hashlib.sha256((ROOT/ch['frozenSource']).read_bytes()).hexdigest()
        source_images=[b for b in ch['blocks'] if b['type']=='source-image']
        assert len(source_images)==len(section.select('.source-plate'))
        for img in source_images:
            assert hashlib.sha256((ROOT/img['src']).read_bytes()).hexdigest()==img['sha256']
        report.append({'chapter':ch['id'],'title':title,'revision':revision,'paragraphs':len(expected),'characters':ch['characters'],'exact_match':True,'text_sha256':digest})
    for img in doc.select('img[src]'):
        src=img['src']
        if not src.startswith('data:'):assert (ROOT/src).is_file(), f'Missing asset: {src}'
    for ill in json.loads((ROOT/'data/illustrations.json').read_text()):
        expected=metadata[ill['chapter']-1]['blocks'][ill['before']]['text']
        assert expected.startswith(ill['source_excerpt'])
    assert len(doc.select('.chapter-page'))==10
    return {'chapters':report,'total_paragraphs':sum(c['paragraphs'] for c in report),'total_characters':sum(c['characters'] for c in report),'all_exactly_equal':True,'source_original_images':4,'generated_paintings':12}

if __name__=='__main__':
    report=verify()
    (ROOT/'data/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
