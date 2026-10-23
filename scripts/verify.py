"""Check every generated text node against the frozen source, including punctuation."""
from pathlib import Path
from bs4 import BeautifulSoup
from import_sources import extract
import hashlib
import json
import re
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]

def verify(html_path=None):
    html_path=Path(html_path or ROOT/'index.html')
    doc=BeautifulSoup(html_path.read_text(),'html.parser')
    embedded=bool(doc.select_one('img[src^="data:"]'))
    metadata=json.loads((ROOT/'data/chapters.json').read_text())
    report=[]
    for ch in metadata:
        title, revision, blocks, notes=extract(ROOT/ch['frozenSource'])
        expected=[b['text'] for b in blocks if 'text' in b]
        section=doc.select_one(f'#chapter-{ch["id"]}')
        actual=[p.get_text() for p in section.select('.original')]
        assert actual==expected, f'Chapter {ch["id"]} differs from frozen source'
        assert ch['title']==title and ch['revision']==revision
        assert ''.join(section.h2.stripped_strings)==''.join(re.split(r'[\s\u3000]+',title,maxsplit=2)[1:])
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
    images=json.loads((ROOT/'data/illustrations.json').read_text())
    assert len({ill['src'] for ill in images})==len(images), 'Illustration asset reused'
    for ill in images:
        expected=metadata[ill['chapter']-1]['blocks'][ill['before']]['text']
        assert ill['source_excerpt'] in expected
        if ill.get('asset_sha256'):
            assert hashlib.sha256((ROOT/ill['src']).read_bytes()).hexdigest()==ill['asset_sha256']
        if not embedded:
            assert len(doc.select(f'#chapter-{ill["chapter"]} .illustration img[src="{ill["src"]}"]'))==1
    assert len(doc.select('.chapter-page'))==len(metadata)==120
    counts=Counter(i['chapter'] for i in images)
    for n in range(1,121): assert len(doc.select(f'#chapter-{n} .illustration'))==counts[n]
    return {'chapters':report,'total_paragraphs':sum(c['paragraphs'] for c in report),'total_characters':sum(c['characters'] for c in report),'all_exactly_equal':True,'source_original_images':sum(sum(b['type']=='source-image' for b in ch['blocks']) for ch in metadata),'generated_paintings':len(images)+1,'illustrated_chapters':len(counts),'chapter_illustration_counts':{str(n):counts[n] for n in range(1,121)},'minimum_illustrations_per_chapter':min(counts[n] for n in range(1,121)),'chapters_with_at_least_three':sum(counts[n]>=3 for n in range(1,121))}

if __name__=='__main__':
    report=verify()
    (ROOT/'data/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
