from pathlib import Path
from fractions import Fraction as Q
import json,time,hashlib,itertools,sys,shutil
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.optimize import root
from algebraic_core import Config,residual_jac
from certification import isolate,rationalize,verify_interval
from verify_record import accept
if not __debug__:raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
OUT=Path(__file__).resolve().parent

def canonical(cfg,x):
    es=[cfg.j,cfg.k,cfg.ell];p=1;groups=[];values=[]
    for exps in es:
        z=sorted(zip(exps,x[p:p+len(exps)]),key=lambda ev:(-ev[0],ev[1]));p+=len(exps)
        groups.append(tuple(e for e,v in z));values.extend(v for e,v in z)
    return Config(*groups),np.array([x[0]]+values+[x[-1]])

def split(cfg,x):
    groups=[list(cfg.j),list(cfg.k),list(cfg.ell)];v=[];p=1
    for e in groups:v.append(list(x[p:p+len(e)]));p+=len(e)
    return groups,v

def neighbors(cfg,x,grow=True):
    exps,values=split(cfg,x)
    if grow:
        for new in range(3):
            old=[k for k in range(3) if k!=new]
            for i,j in itertools.product(range(len(exps[old[0]])),range(len(exps[old[1]]))):
                e=[z[:] for z in exps];v=[z[:] for z in values]
                e[old[0]][i]+=1;e[old[1]][j]+=1;e[new].append(1)
                v[new].append(np.sqrt(v[old[0]][i]*v[old[1]][j]))
                c=Config(*map(tuple,e));xx=np.array([x[0]]+sum(v,[])+[x[-1]])
                if c.valid():yield (*canonical(c,xx),f'grow:new={new},existing={i},{j}')
        # Include the fixed Z frequency zero: grow its multiplicity by one,
        # together with a new A/B frequency and one exponent in the other.
        for new in (0,1):
            other=1-new
            for i in range(len(exps[other])):
                for scale in (.25,.75):
                    e=[z[:] for z in exps];v=[z[:] for z in values]
                    e[other][i]+=1;e[new].append(1)
                    v[new].append(max(.001,scale*v[other][i]))
                    c=Config(*map(tuple,e));xx=np.array([x[0]]+sum(v,[])+[x[-1]])
                    if c.valid():yield (*canonical(c,xx),f'grow_zero:new={new},existing={i},scale={scale}')
    else:
        # Balanced split in one family and merge in another; total degree and
        # equation/variable count unchanged. Includes near-symmetric splitting.
        for f,g in itertools.permutations(range(3),2):
            for i,m in enumerate(exps[f]):
                for m1 in range(1,m//2+1):
                    for j,k in itertools.combinations(range(len(exps[g])),2):
                        e=[z[:] for z in exps];v=[z[:] for z in values]
                        e[f][i]=m1;e[f].append(m-m1);base=v[f][i];v[f][i]=base*.94;v[f].append(base*1.06)
                        merged=(v[g][j]*e[g][j]+v[g][k]*e[g][k])/(e[g][j]+e[g][k])
                        e[g][j]+=e[g][k];v[g][j]=merged;del e[g][k];del v[g][k]
                        c=Config(*map(tuple,e));xx=np.array([x[0]]+sum(v,[])+[x[-1]])
                        if c.valid():yield (*canonical(c,xx),f'splitmerge:{f},{i},{m1};{g},{j},{k}')
        # Move one origin factor into a new positive Z frequency, balancing
        # the added variable by merging two A or B frequencies.
        if cfg.zero_power_t>0 and values[2]:
            for g in (0,1):
                for j,k in itertools.combinations(range(len(exps[g])),2):
                    e=[z[:] for z in exps];v=[z[:] for z in values]
                    e[2].append(1);v[2].append(max(.001,min(values[2])*.25))
                    merged=(v[g][j]*e[g][j]+v[g][k]*e[g][k])/(e[g][j]+e[g][k])
                    e[g][j]+=e[g][k];v[g][j]=merged;del e[g][k];del v[g][k]
                    c=Config(*map(tuple,e));xx=np.array([x[0]]+sum(v,[])+[x[-1]])
                    if c.valid():yield (*canonical(c,xx),f'origin_split_merge:{g},{j},{k}')
        # Conversely absorb a positive Z factor into the origin and split A/B.
        for k in range(len(exps[2])):
            for f in (0,1):
                for i,m in enumerate(exps[f]):
                    for m1 in range(1,m//2+1):
                        e=[z[:] for z in exps];v=[z[:] for z in values]
                        del e[2][k];del v[2][k]
                        e[f][i]=m1;e[f].append(m-m1);base=v[f][i];v[f][i]=base*.94;v[f].append(base*1.06)
                        c=Config(*map(tuple,e));xx=np.array([x[0]]+sum(v,[])+[x[-1]])
                        if c.valid():yield (*canonical(c,xx),f'origin_absorb_split:{k};{f},{i},{m1}')

def key(c):return str((c.j,c.k,c.ell))

def parent_growth_starts(target,numerical,parents,limit=3):
    target,numerical=canonical(target,numerical)
    starts=[];seen=set()
    for pc,px,pid in parents:
        if pc.degree!=target.degree-2:continue
        for nc,nx,move in neighbors(pc,px,True):
            nc,nx=canonical(nc,nx)
            if nc!=target:continue
            fingerprint=tuple(np.round(nx,10))
            if fingerprint in seen:continue
            seen.add(fingerprint)
            distance=float(np.linalg.norm((nx-numerical)/np.maximum(abs(numerical),.1)))
            starts.append((distance,nx,pid+':'+move))
    return sorted(starts,key=lambda v:v[0])[:limit]

def solve(c,x,maxfev=450):
    sx=np.maximum(abs(x),.1);f,j=residual_jac(x,c);sf=np.maximum(np.sum(abs(j)*sx,axis=1),1e-12)
    def fj(z):
        f,j=residual_jac(z*sx,c);return f/sf,j*sx/sf[:,None]
    ans=root(fj,x/sx,jac=True,method='hybr',options={'xtol':2e-10,'maxfev':maxfev})
    xx=ans.x*sx;f,j=fj(ans.x);res=float(max(abs(f)))
    cond=float(np.linalg.cond(j));delta=float(np.sqrt((2-xx[0])/4)) if -2<xx[0]<2 else None
    ok=bool(np.all(xx[1:]>1e-8) and delta is not None and res<2e-11)
    return xx,{'numerical_quasi_delta':delta,'scaled_residual':res,'jacobian_condition_scaled':cond,
               'solver_success':bool(ans.success),'nfev':int(ans.nfev),'numerical_success':ok}

def solve_job(payload):
    nc,trial,origin,phase,restart=payload;t=time.perf_counter()
    try:xx,info=solve(nc,trial)
    except Exception as exc:xx=trial;info={'numerical_success':False,'error':repr(exc)}
    return nc,xx,origin,phase,restart,info,time.perf_counter()-t

def main():
    executor=ProcessPoolExecutor(max_workers=6)
    rng=np.random.default_rng(20260916);start=time.perf_counter();inc=Q(103,105);bestq=Q(0)
    state={'starting_certified_delta':str(inc),'external_baseline':'2452087/2500000','layers':[],
           'frontier':[],'records':[],'stopping_reason':None}
    seed=json.loads((OUT.parent/'gbcp_charles_boston_20260915/crossing_high_precision.json').read_text())
    c=Config(*[tuple(seed['configuration'][k]) for k in ('j','k','ell')]);c,x=canonical(c,np.array(list(map(float,seed['root']))))
    parents=[(c,x,'starting_degree22')];nodes=0;no_improve=0;tiny=0
    resume=(OUT/'state.json').exists()
    startdegree=24;offset=0
    if resume:
        state=json.loads((OUT/'state.json').read_text());inc=Q(state['incumbent_certified_delta']);bestq=Q(state['incumbent_quasi_lower'])
        offset=state['elapsed_seconds'];last=state['layers'][-1]
        startdegree=last['degree']+2;no_improve=last['consecutive_no_improvement'];tiny=last['consecutive_tiny_quasi_improvement']
        nodes=max(int(n['id'].split('_')[0][1:]) for n in state['frontier'])
        parents=[]
        for node in state['frontier']:
            if node['degree']==last['degree'] and node['interval_certified']:
                cfg=Config(*[tuple(node['configuration'][k]) for k in ('j','k','ell')])
                parents.append((cfg,np.array(list(map(float,node['quasi_root']))),node['id']))
        if state.get('next_parent_seeds'):
            parents=[(Config(*[tuple(v['configuration'][k]) for k in ('j','k','ell')]),np.array(v['root']),v['source']) for v in state['next_parent_seeds']]
        if not parents:raise RuntimeError('Resume needs saved certified parents')
        state['stopping_reason']=None
        state.setdefault('policy_updates',[]).append({'from_degree':startdegree,'policy':'include variable origin multiplicity; six numerical workers; exact GMP with stdlib cross-check'})
    def save():
        state['incumbent_certified_delta']=str(inc);state['incumbent_quasi_lower']=str(bestq);state['elapsed_seconds']=offset+time.perf_counter()-start
        temporary=OUT/'state.tmp'
        temporary.write_text(json.dumps(state,indent=2,allow_nan=False))
        temporary.replace(OUT/'state.json')
    def certify(c,x,origin):
        nonlocal inc,bestq,nodes
        cached=[n for n in state['frontier'] if n['degree']==c.degree and n['configuration']==c.data() and 'seconds' in n]
        positive=next((n for n in cached if n['interval_certified']),None)
        if positive:
            verify_interval(json.loads((OUT/'nodes'/positive['id']/'interval.json').read_text()))
            print('REUSE CERTIFIED NODE',positive['id'],flush=True)
            return c,np.array(list(map(float,positive['quasi_root']))),positive['id']
        if any(n['initial_source']==origin for n in cached):return None
        nodes+=1;nodeid=f'n{nodes:04d}_d{c.degree}';folder=OUT/'nodes'/nodeid
        print('ISOLATE',nodeid,flush=True);t=time.perf_counter();data=isolate(c,x,folder)
        primary_failed=not bool(data);parent_trials=[]
        if primary_failed:
            for index,(distance,nx,source) in enumerate(parent_growth_starts(c,x,parents)):
                trial_folder=folder/'direct_parent_trials'/f'trial_{index}'
                print('DIRECT PARENT RETRY',nodeid,index,source,flush=True)
                data=isolate(c,nx,trial_folder,(180,280))
                parent_trials.append({'source':source,'start':nx.tolist(),'distance_to_numerical_start':distance,
                                      'interval_certified':bool(data),'directory':str(trial_folder.relative_to(OUT))})
                if data:
                    for name in ('interval.json','interval_check.json','quasi.json'):
                        shutil.copyfile(trial_folder/name,folder/name)
                    break
        node={'id':nodeid,'degree':c.degree,'configuration':c.data(),'initial_source':origin,
              'numerical_start':x.tolist(),
              'interval_certified':bool(data),'strict_rational_witness':False,'final_certified_delta':None}
        if primary_failed:
            node['initial_isolation_failed']=True
            node['direct_parent_growth_trials']=parent_trials
        state['frontier'].append(node)
        if data:
            qlo=Q(json.loads((folder/'interval.json').read_text())['delta_interval'][0]);bestq=max(bestq,qlo)
            node['quasi_delta_interval']=json.loads((folder/'interval.json').read_text())['delta_interval']
            node['quasi_root']=data['root']
            if qlo>inc:
                for places in (8,16):
                    t1=time.perf_counter()
                    try:
                        for coefficient_digits in (0,c.degree*(places+2)+40,2*c.degree*(places+2)+80):
                            try:
                                path=rationalize(c,data['root'],places,folder,minimum_digits=coefficient_digits);check=accept(path)
                                break
                            except Exception as precision_error:
                                node.setdefault('coefficient_precision_retries',[]).append({'places':places,'minimum_digits':coefficient_digits,'error':repr(precision_error)})
                                if coefficient_digits==2*c.degree*(places+2)+80:raise
                        e=Q(check['delta'])
                        node['strict_rational_witness']=True;node['final_certified_delta']=str(e)
                        if e>inc:
                            inc=e;state['best_configuration']=c.data();state['best_witness']=str(path.relative_to(OUT))
                            state['records'].append({'node':nodeid,'delta':str(e),'witness':str(path.relative_to(OUT)),
                                                     'sha256':check['sha256'],'seconds':time.perf_counter()-t1})
                            print('NEW EXACT INCUMBENT',float(e),str(e),nodeid,flush=True);save()
                    except Exception as exc:
                        node.setdefault('rational_failures',[]).append({'places':places,'error':repr(exc)})
                        print('RATIONAL FAILED',nodeid,places,repr(exc),flush=True)
            node['seconds']=time.perf_counter()-t;save()
            return c,np.array(list(map(float,data['root']))),nodeid
        node['seconds']=time.perf_counter()-t;save();return None
    if not resume:
        p=certify(c,x,'audited_seed');parents=[p] if p else parents
    for degree in itertools.count(startdegree,2):
        node_degrees={n['id']:n['degree'] for n in state['frontier']}
        previous_records=[r for r in state['records'] if node_degrees[r['node']]<degree]
        oldinc=max([Q(state['starting_certified_delta'])]+[Q(r['delta']) for r in previous_records])
        oldq=max([Q(0)]+[Q(n['quasi_delta_interval'][0]) for n in state['frontier'] if n['degree']<degree and n.get('interval_certified')])
        attempts=0;pool=[];grouped={};successcount=0;certcount=0;records_start=len(previous_records)
        # Expand every growth edge from each of the retained certified parents.
        for pc,px,pid in parents:
            for nc,nx,move in neighbors(pc,px,True):grouped.setdefault(key(nc),[]).append((nc,nx,pid+':'+move))
        if not grouped:raise RuntimeError('empty frontier without justified stopping condition')
        num_growth=len(grouped);seen_cfg=set();warm_success=[]
        logpath=OUT/f'attempts_degree_{degree}.jsonl';completed=set();completed_lateral_keys=set()
        numerical_phase_complete=any(n['degree']==degree for n in state['frontier'])
        if logpath.exists():
            for line in logpath.read_text().splitlines():
                r=json.loads(line);cc=Config(*[tuple(r['configuration'][k]) for k in ('j','k','ell')])
                completed.add((key(cc),r['initial_source'],r['restart']));attempts+=1;seen_cfg.add(key(cc))
                if r['phase']=='balanced_split_merge':completed_lateral_keys.add(key(cc))
                if r.get('numerical_success'):
                    successcount+=1;xx=np.array(r['root']);cc,xx=canonical(cc,xx)
                    if not any(cc==other[0] and abs(xx[0]-other[1][0])<2e-9 for other in pool):pool.append((cc,xx,r['initial_source']))
        log=logpath.open('a',encoding='utf-8')
        def run_batch(groups,phase):
            nonlocal attempts,successcount
            jobs=[]
            for cfgkey,seeds in groups.items():
                seen_cfg.add(cfgkey);seen_seeds=set();best_seed=seeds[0];bestres=float('inf')
                if phase=='balanced_split_merge':
                    # Historical layers: no record came from this operator.
                    # Still cover every unique configuration, but rank equivalent
                    # warm-start assignments by the initial normalized residual.
                    def score(seed):
                        cc,xx,_=seed;ff,jj=residual_jac(xx,cc)
                        return float(max(abs(ff)/np.maximum(np.sum(abs(jj)*np.maximum(abs(xx),.1),axis=1),1e-12)))
                    seeds=sorted(seeds,key=score)[:2]
                for nc,nx,origin in seeds:
                    sk=tuple(np.round(nx,7))
                    if sk in seen_seeds:continue
                    seen_seeds.add(sk)
                    for restart in range(2):
                        if (cfgkey,origin,restart) in completed:continue
                        trial=nx.copy()
                        if restart:trial[1:]*=np.exp(rng.normal(0,.035,size=len(nx)-1))
                        jobs.append((nc,trial,origin,phase,restart))
            # Ordered collection preserves deterministic seeds and tie-breaking.
            for nc,xx,origin,phase,restart,info,elapsed in executor.map(solve_job,jobs,chunksize=1):
                attempts+=1
                rec={'degree':degree,'configuration':nc.data(),'initial_source':origin,'phase':phase,'restart':restart,
                     **info,'root':xx.tolist(),'seconds':elapsed}
                encoded=json.dumps(rec,default=str);log.write(encoded+'\n');log.flush()
                if info.get('numerical_success'):
                    successcount+=1;cc,xx=canonical(nc,xx)
                    if not any(cc==other[0] and abs(xx[0]-other[1][0])<2e-9 for other in pool):
                        pool.append((cc,xx,origin));print('NUMERIC',degree,info['numerical_quasi_delta'],key(cc),flush=True)
                if attempts%40==0:print('PROGRESS',degree,phase,attempts,'unique roots',len(pool),flush=True)
        if not numerical_phase_complete:run_batch(grouped,'growth')
        # Several branches, not just the current best. Explore all balanced
        # split/merge neighbors of the top three numerical growth solutions.
        pool.sort(key=lambda z:z[1][0]);laterals={}
        bases=[];base_configs=set()
        for candidate in pool:
            if key(candidate[0]) not in base_configs:
                bases.append(candidate);base_configs.add(key(candidate[0]))
            if len(bases)>=3:break
        if not bases:bases=[v[0] for v in grouped.values()][:3]
        for pc,px,pid in bases:
            for nc,nx,move in neighbors(pc,px,False):laterals.setdefault(key(nc),[]).append((nc,nx,pid+':'+move))
        if not numerical_phase_complete:run_batch(laterals,'balanced_split_merge')
        else:
            laterals={k:[] for k in completed_lateral_keys}
            print('REUSE COMPLETED NUMERICAL PHASE',degree,attempts,'attempts',flush=True)
        log.close()
        pool.sort(key=lambda z:z[1][0]);newparents=[]
        # Try the best candidates first; retain up to three isolated distinct
        # configurations, keeping every other numerical result as untrusted log.
        tried_configs=set()
        for pc,px,pid in pool:
            if key(pc) in tried_configs:continue
            tried_configs.add(key(pc));p=certify(pc,px,pid)
            if p:newparents.append(p);certcount+=1
            if len(newparents)>=3:break
        if newparents:parents=newparents
        else:
            # Advance all-degree coverage using three best unproved warm starts.
            parents=(pool[:3] if pool else [v[0] for v in grouped.values()][:3])
        improved=inc>oldinc;no_improve=0 if improved else no_improve+1
        gain=bestq-oldq
        # Absence of an isolated root is not evidence of a small quasi gain.
        # Compare the upper endpoint against the previous lower endpoint.
        gain_upper=max([Q(node['quasi_delta_interval'][1]) for node in state['frontier'] if node.get('interval_certified')])-oldq
        tiny=tiny+1 if certcount>0 and gain_upper<Q(1,10**6) else 0
        layer={'degree':degree,'unique_configurations':len(seen_cfg),'growth_configurations':num_growth,
               'balanced_split_merge_configurations':len(laterals),'attempts':attempts,'numerical_successes':successcount,
               'distinct_numerical_roots':len(pool),'interval_certified_solutions':certcount,
               'rational_record_witnesses':len(state['records'])-records_start,'certified_improvement':improved,
               'best_quasi_improvement_lower_endpoint':str(gain),'consecutive_no_improvement':no_improve,
               'consecutive_tiny_quasi_improvement':tiny}
        state['next_parent_seeds']=[{'configuration':pc.data(),'root':px.tolist(),'source':pid,
                                    'role':'warm start only; formal status is in the node certificate'} for pc,px,pid in parents]
        state['layers'].append(layer);save();print('LAYER COMPLETE',json.dumps(layer),flush=True)
        if (OUT/'pause_after_layer').exists():
            print('CHECKPOINT PAUSE REQUESTED',flush=True);executor.shutdown();return
        if no_improve>=4:state['stopping_reason']='condition 1: four consecutive degree increments without certified improvement';save();break
        if tiny>=3:state['stopping_reason']='condition 2: three consecutive degree increments with certified quasi improvement < 1e-6';save();break
    executor.shutdown();print('ROUTE STOPPED',state['stopping_reason'],flush=True)

if __name__=='__main__':main()
