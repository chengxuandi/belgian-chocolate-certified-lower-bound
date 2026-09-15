"""Cross-process Python/GMP proposal comparison with exact proof replay."""
from pathlib import Path
import os,sys,json,subprocess,time,hashlib
OUT=Path(__file__).resolve().parent
def child():
    sys.path.insert(0,str(OUT/'vendor'))
    import mpmath as mp
    from mpmath.libmp.backend import BACKEND
    from algebraic_core import Config
    from certification import MP,circuit,refine,verify_interval
    mp.mp.dps=180;rows=[]
    for node in ('n0001_d22','n0062_d64','n0072_d68'):
        data=json.loads((OUT/'nodes'/node/'quasi.json').read_text())
        cfg=Config(*[tuple(data['configuration'][k]) for k in ('j','k','ell')])
        x=list(map(mp.mpf,data['root']));t=time.perf_counter()
        for _ in range(8):f,J=circuit(x,cfg,MP)
        calc=time.perf_counter()-t
        serialized=json.dumps([[mp.nstr(v,170) for v in f],[[mp.nstr(v,170) for v in row] for row in J]])
        t=time.perf_counter();root=refine(cfg,data['root'],180);refinement=time.perf_counter()-t
        check=verify_interval(json.loads((OUT/'nodes'/node/'interval.json').read_text()))
        rows.append({'node':node,'F_J_sha256':hashlib.sha256(serialized.encode()).hexdigest(),
                     'root':[mp.nstr(v,140) for v in root],
                     'circuit_seconds':calc,'refine_seconds':refinement,'interval_check':check})
    print(json.dumps({'backend':BACKEND,'cases':rows}))
def main():
    results=[]
    for backend in ('python','gmpy'):
        env=os.environ.copy()
        if backend=='python':env['MPMATH_NOGMPY']='1'
        else:env.pop('MPMATH_NOGMPY',None)
        result=json.loads(subprocess.check_output([sys.executable,str(Path(__file__)),'--child'],env=env,text=True))
        assert result['backend']==backend;results.append(result)
    for a,b in zip(results[0]['cases'],results[1]['cases']):
        assert a['F_J_sha256']==b['F_J_sha256'] and a['root']==b['root'] and a['interval_check']==b['interval_check']
    (OUT/'mpmath_backend_review.json').write_text(json.dumps({'status':'PASS','comparisons':results},indent=2))
    print(json.dumps([{'backend':v['backend'],'timings':[(c['node'],c['circuit_seconds'],c['refine_seconds']) for c in v['cases']]} for v in results],indent=2))
if __name__=='__main__':child() if '--child' in sys.argv else main()
