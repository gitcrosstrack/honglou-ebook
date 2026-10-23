"""Add source-anchored scenes without changing the frozen novel text."""
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
STYLE=('Use case: historical-scene. Asset: one narrative illustration for Dream of the Red Chamber. '
       'Exquisite traditional Chinese gongbi fine contours with subtle ink wash, warm antique xuan paper, '
       'muted jade and smoky grey mineral pigments with restrained cinnabar accents. Wide landscape 3:2. '
       'Keep period Chinese clothing and architecture, fully clothed figures, graceful small figures within a spacious composition. '
       'Paint only the stated benign moment in this chapter, no events from other chapters. '
       'No modern objects, photography, readable text, calligraphy, seals, watermark, frame or border. ')

def add(specs):
    chapters=json.loads((ROOT/'data/chapters.json').read_text())
    file=ROOT/'data/extended-illustration-plan.json'
    plans=json.loads(file.read_text()) if file.exists() else []
    original=json.loads((ROOT/'data/illustrations.json').read_text())
    for spec in specs:
        ch=chapters[spec['chapter']-1]
        matches=[(i,b) for i,b in enumerate(ch['blocks']) if spec['match'] in b.get('text','')]
        assert len(matches)==1, (spec['chapter'],spec['match'],len(matches))
        before,block=matches[0]
        count=sum(i['chapter']==spec['chapter'] and not i.get('id','').startswith('dense-') for i in original)
        number=count+sum(p['chapter']==spec['chapter'] for p in plans)+1
        assert number<=3, ('Too many scenes',spec['chapter'])
        scene_id=f'dense-{spec["chapter"]:03d}-{number}'
        assert not any(p['id']==scene_id for p in plans)
        excerpt=spec.get('excerpt',spec['match'])
        assert excerpt in block['text']
        plan={'id':scene_id,'chapter':spec['chapter'],'before':before,'title':spec['title'],
              'alt':spec['description'],'scene':spec['title'],'source_excerpt':excerpt,
              'prompt':STYLE+f'Chapter {spec["chapter"]}. Scene: '+spec['description']}
        plans.append(plan)
    file.write_text(json.dumps(plans,ensure_ascii=False,indent=2))
    print(json.dumps({'planned_new_images':len(plans),'last_id':plans[-1]['id']},ensure_ascii=False))

if __name__=='__main__': add(json.load(sys.stdin))
