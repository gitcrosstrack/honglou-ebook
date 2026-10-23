"""Persist one additional illustration safely; never replace an existing painting."""
from pathlib import Path
from collections import Counter
from PIL import Image
import argparse,json,hashlib
from accept_image import write_json

ROOT=Path(__file__).resolve().parents[1]

def progress(illustrations):
    counts=Counter(i['chapter'] for i in illustrations)
    return {'target_per_chapter':3,'total_chapters':120,'chapter_image_counts':{str(n):counts[n] for n in range(1,121)},
            'chapters_at_target':[n for n in range(1,121) if counts[n]>=3],
            'total_chapter_illustrations':len(illustrations),'remaining_images':sum(max(0,3-counts[n]) for n in range(1,121)),
            'next_chapter':next((n for n in range(1,121) if counts[n]<3),None),'stopped_on_rate_limit':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--id',required=True);parser.add_argument('--image',required=True);args=parser.parse_args()
    plans=json.loads((ROOT/'data/extended-illustration-plan.json').read_text());plan=next(p for p in plans if p['id']==args.id)
    illustrations=json.loads((ROOT/'data/illustrations.json').read_text())
    assert not any(i.get('id')==args.id for i in illustrations),'Already accepted'
    asset='assets/'+args.id+'.webp';assert not (ROOT/asset).exists(),'Asset exists; inspect before retrying'
    ch=json.loads((ROOT/'data/chapters.json').read_text())[plan['chapter']-1]
    assert plan['source_excerpt'] in ch['blocks'][plan['before']]['text']
    with Image.open(args.image) as im: im.save(ROOT/asset,quality=86,method=6)
    entry={key:plan[key] for key in ['id','chapter','before','title','alt','scene','source_excerpt']};entry['src']=asset
    entry['asset_sha256']=hashlib.sha256((ROOT/asset).read_bytes()).hexdigest();illustrations.append(entry)
    write_json(ROOT/'data/illustrations.json',illustrations)
    prompts=json.loads((ROOT/'data/image-prompts.json').read_text());prompts.append({'id':args.id,'prompt':plan['prompt'],'phase':'generated'})
    write_json(ROOT/'data/image-prompts.json',prompts)
    result=progress(illustrations);write_json(ROOT/'data/density-progress.json',result)
    print(json.dumps({'accepted':args.id,'chapters_at_target':len(result['chapters_at_target']),'remaining_images':result['remaining_images']}))
