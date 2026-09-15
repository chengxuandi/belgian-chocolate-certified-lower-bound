"""Fill missing same-degree configuration neighbors of retained certified nodes.
This supplements the best-first main search; it never promotes floating results.
"""
from pathlib import Path
import json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from frontier_search import Config,neighbors,solve_job,key
OUT=Path(__file__).resolve().parent
def main():
    state=json.loads((OUT/'state.json').read_text());maxdegree=state['layers'][-1]['degree'];seen={};done=set();trace=[]
    for path in list(OUT.glob('attempts_degree_*.jsonl'))+[OUT/'adjacency_completion.jsonl']:
        if not path.exists():continue
        for line in path.read_text().splitlines():
            r=json.loads(line);c=Config(*[tuple(r['configuration'][k]) for k in ('j','k','ell')]);seen.setdefault(c.degree,set()).add(key(c))
            done.add((key(c),r['initial_source'],r['restart']))
    jobs=[];rng=np.random.default_rng(984297)
    for node in state['frontier']:
        if not node.get('interval_certified') or node['degree']>maxdegree:continue
        c=Config(*[tuple(node['configuration'][k]) for k in ('j','k','ell')]);x=np.array(list(map(float,node['quasi_root'])));required={}
        for nc,nx,move in neighbors(c,x,False):
            required.setdefault(key(nc),(nc,nx,node['id']+':coverage:'+move))
        missing=set(required)-seen.setdefault(c.degree,set())
        trace.append({'node':node['id'],'degree':c.degree,'required_distinct_lateral_configurations':len(required),'newly_scheduled_configurations':len(missing)})
        for k in sorted(missing):
            nc,nx,origin=required[k];seen[c.degree].add(k)
            for restart in (0,1):
                if (k,origin,restart) in done:continue
                trial=nx.copy()
                if restart:trial[1:]*=np.exp(rng.normal(0,.035,len(nx)-1))
                jobs.append((nc,trial,origin,'adjacency_completion',restart))
    print('Missing adjacency attempts scheduled',len(jobs),'through degree',maxdegree,flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool,(OUT/'adjacency_completion.jsonl').open('a') as stream:
        for i,(nc,xx,origin,phase,restart,info,elapsed) in enumerate(pool.map(solve_job,jobs,chunksize=1)):
            result={'degree':nc.degree,'configuration':nc.data(),'initial_source':origin,'phase':phase,'restart':restart,**info,'root':xx.tolist(),'seconds':elapsed}
            stream.write(json.dumps(result)+'\n');stream.flush()
            if info.get('numerical_success'):print('SUPPLEMENTAL NUMERIC',nc.degree,info['numerical_quasi_delta'],key(nc),flush=True)
            if i%200==0:print('SUPPLEMENTAL PROGRESS',i,flush=True)
    (OUT/'adjacency_coverage_review.json').write_text(json.dumps({'through_degree':maxdegree,'nodes':trace,'scheduled_attempts':len(jobs),'complete':True},indent=2))
    print('Adjacency completion finished',flush=True)
if __name__=='__main__':main()
