"""Fetch missing chapter snapshots; never overwrite frozen sources."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def fetch(number):
    dest=ROOT/'sources'/f'chapter-{number:02d}.html'
    if dest.exists():return number,'retained'
    url=f'https://zh.wikisource.org/zh-hans/%E7%B4%85%E6%A8%93%E5%A4%A2/%E7%AC%AC{number:03d}%E5%9B%9E'
    temporary=dest.with_suffix('.download')
    subprocess.run(['curl','-fsSL','--retry','2','--max-time','50','-A','Mozilla/5.0',url,'-o',str(temporary)],check=True)
    assert temporary.stat().st_size>10000
    temporary.rename(dest)
    return number,'downloaded'

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(fetch,n) for n in range(1,121)]
        for future in as_completed(futures):
            number,status=future.result()
            print(number,status,flush=True)
