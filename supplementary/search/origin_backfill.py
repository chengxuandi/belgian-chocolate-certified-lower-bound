"""Supplemental numerical coverage of origin-growth edges at earlier degrees.
Does not modify the formal frontier, incumbent, or certificates.
"""
from pathlib import Path
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from frontier_search import Config,neighbors,solve_job,key
OUT=Path(__file__).resolve().parent
def main():
    state=json.loads((OUT/'state.json').read_text());jobs=[]
    for node in state['frontier']:
        if not node.get('interval_certified') or node['degree']>38:continue
        c=Config(*[tuple(node['configuration'][k]) for k in ('j','k','ell')]);x=np.array(list(map(float,node['quasi_root'])))
        for nc,nx,move in neighbors(c,x,True):
            if not move.startswith('grow_zero:'):continue
            jobs.append((nc,nx,node['id']+':'+move,'origin_backfill',0))
    log=OUT/'origin_backfill.jsonl'
    with ProcessPoolExecutor(max_workers=2) as pool,log.open('w') as stream:
        for nc,xx,origin,phase,restart,info,elapsed in pool.map(solve_job,jobs,chunksize=1):
            result={'degree':nc.degree,'configuration':nc.data(),'initial_source':origin,'phase':phase,'restart':restart,
                    **info,'root':xx.tolist(),'seconds':elapsed}
            stream.write(json.dumps(result)+'\n');stream.flush()
            if info.get('numerical_success'):print(nc.degree,info['numerical_quasi_delta'],key(nc),flush=True)
    print('Origin backfill finished',len(jobs),flush=True)
if __name__=='__main__':main()
