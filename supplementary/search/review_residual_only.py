"""Check a proposal-only speed change: skip unused Jacobian construction."""
from pathlib import Path
from fractions import Fraction as Q
import json,time
import mpmath as mp
from algebraic_core import Config
from certification import MP,Dyadic,circuit,verify_interval
OUT=Path(__file__).resolve().parent
mp.mp.dps=150
rows=[]
for node in ('n0001_d22','n0062_d64','n0072_d68'):
    data=json.loads((OUT/'nodes'/node/'quasi.json').read_text())
    cfg=Config(*[tuple(data['configuration'][k]) for k in ('j','k','ell')])
    x=list(map(mp.mpf,data['root']))
    t=time.perf_counter()
    for _ in range(10):f,J=circuit(x,cfg,MP)
    full=time.perf_counter()-t
    t=time.perf_counter()
    for _ in range(10):ff,JJ=circuit(x,cfg,MP,derivatives=False)
    residual=time.perf_counter()-t
    assert f==ff and JJ is None
    cert=json.loads((OUT/'nodes'/node/'interval.json').read_text())
    ar=Dyadic(cert['bits']);r=int(cert['radius'])
    box=[(int(v)-r,int(v)+r) for v in cert['center']]
    assert circuit(box,cfg,ar)[0]==circuit(box,cfg,ar,derivatives=False)[0]
    verify_interval(cert)
    rows.append({'node':node,'full_seconds':full,'residual_only_seconds':residual,
                 'mp_residual_identical':True,'exact_interval_residual_identical':True,
                 'existing_interval_certificate_passed':True})
(OUT/'residual_only_review.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
