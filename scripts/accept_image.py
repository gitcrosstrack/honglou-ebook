"""Persist an accepted generated image and its exact source correspondence."""
from pathlib import Path
from PIL import Image
import argparse,json

ROOT=Path(__file__).resolve().parents[1]

def write_json(path,value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2))
    temporary.replace(path)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--chapter',type=int,required=True)
    parser.add_argument('--image',required=True)
    args=parser.parse_args()
    plans=json.loads((ROOT/'data/illustration-plan.json').read_text())
    plan=next(p for p in plans if p['chapter']==args.chapter)
    ch=json.loads((ROOT/'data/chapters.json').read_text())[args.chapter-1]
    asset=f'assets/chapter-{args.chapter:02d}.webp'
    Image.open(args.image).save(ROOT/asset,quality=86,method=6)
    illustrations=json.loads((ROOT/'data/illustrations.json').read_text())
    assert not any(i['chapter']==args.chapter for i in illustrations),'Chapter image already accepted'
    entry={key:plan[key] for key in ['chapter','before','title','alt','scene']}
    entry.update(src=asset,source_excerpt=ch['blocks'][plan['before']]['text'][:65])
    illustrations.append(entry)
    write_json(ROOT/'data/illustrations.json',illustrations)
    prompts=json.loads((ROOT/'data/image-prompts.json').read_text())
    prompts.append({'id':args.chapter,'prompt':plan['prompt'],'phase':'generated'})
    write_json(ROOT/'data/image-prompts.json',prompts)
    completed=sorted({i['chapter'] for i in illustrations})
    write_json(ROOT/'data/render-progress.json',{'total_chapters':120,'illustrated_chapters':completed,'next_chapter':next((i for i in range(1,121) if i not in completed),None),'stopped_on_rate_limit':False})
    print(json.dumps({'chapter':args.chapter,'asset':asset,'accepted':True,'illustrated_chapters':len(completed)}))
