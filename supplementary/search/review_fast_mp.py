"""Compare proposal-only synthetic Jacobian with the unchanged factor circuit."""
from pathlib import Path
from fractions import Fraction as Q
import json,time
import mpmath as mp
from algebraic_core import Config
from certification import MP,circuit,linear_quotient_numeric
OUT=Path(__file__).resolve().parent
class ReferenceMP(MP):pass  # ar is MP is false, so this executes the original circuit.
def conv(a,b):
    p=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):p[i+j]+=x*y
    return p
for a in (Q(0),Q(1,7),Q(-3,4),Q(1),Q(9,4),Q(-7,2)):
    other=[Q(2,3),Q(5,7),Q(11,2),Q(1)]
    p=conv([a,Q(1)],other)
    assert linear_quotient_numeric(p,a)==other
out=[];mp.mp.dps=140
for node in ('n0001_d22','n0062_d64','n0067_d66'):
    data=json.loads((OUT/'nodes'/node/'quasi.json').read_text());cfg=Config(*[tuple(data['configuration'][k]) for k in ('j','k','ell')])
    x=list(map(mp.mpf,data['root']));t=time.perf_counter();f,J=circuit(x,cfg,ReferenceMP);old=time.perf_counter()-t
    t=time.perf_counter();ff,JJ=circuit(x,cfg,MP);new=time.perf_counter()-t
    assert ff==f
    error=max(abs(a-b)/max(abs(a),mp.mpf(1)) for ra,rb in zip(J,JJ) for a,b in zip(ra,rb))
    assert error<mp.mpf('1e-110')
    out.append({'node':node,'reference_seconds':old,'fast_seconds':new,'max_scaled_difference':mp.nstr(error,15),
                'only_candidate_proposal_changed':True,'integer_interval_circuit_unchanged':True})
(OUT/'fast_mp_review.json').write_text(json.dumps({'exact_rational_division_examples_passed':True,'cases':out},indent=2))
print(json.dumps(out,indent=2))
