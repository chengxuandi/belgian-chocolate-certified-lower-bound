from pathlib import Path
import sys,json,copy,itertools
from fractions import Fraction as Q
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'core'))
import verify_final_witness as primary
import audit_final_witness as audit
def determinant(m):
    result=0
    for p in itertools.permutations(range(len(m))):
        v=(-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
        for i,j in enumerate(p):v*=m[i][j]
        result+=v
    return result
tests=[]
for n in range(1,7):
    c=[1]
    for r in range(1,n+1):
        d=[0]*(len(c)+1)
        for i,v in enumerate(c):d[i]+=r*v;d[i+1]+=v
        c=d
    a=c[::-1]
    H=[[a[2*j-i+1] if 0<=2*j-i+1<=n else 0 for j in range(n)] for i in range(n)]
    expected=[determinant([row[:k] for row in H[:k]]) for k in range(1,n+1)]
    assert primary.hurwitz_minors(c)==expected
    assert len(audit.routh_test(c))==n+1
    tests.append('stable product degree '+str(n)+': explicit permutation determinants and Routh agree')
for c in ([2,1,1,1],[1,0,1],[-1,1]):
    for function in (primary.hurwitz_minors,audit.routh_test):
        try:function(c)
        except (ValueError,ArithmeticError):pass
        else:raise AssertionError('unstable/boundary polynomial accepted')
    tests.append('both reject '+str(c))
obj=primary.read_certificate(BASE/'core/WITNESS_FINAL.txt')
for mode in ('one_integer_changed','wrong_delta','reversed_arrays'):
    changed=copy.deepcopy(obj)
    if mode=='one_integer_changed':changed['x']['numerators_ascending'][0]=str(int(changed['x']['numerators_ascending'][0])+1)
    if mode=='wrong_delta':changed['delta']=str(Q(obj['delta'])+Q(1,10**18))
    if mode=='reversed_arrays':
        for k in ('x','y','p'):changed[k]['numerators_ascending'].reverse()
    e,ps=primary.reconstruct(changed)
    try:primary.identity(e,ps)
    except ValueError:pass
    else:raise AssertionError('primary accepted mutation')
    mappings={k:{i:Q(int(v),int(changed[k]['denominator'])) for i,v in enumerate(changed[k]['numerators_ascending']) if int(v)} for k in ('x','y','p')}
    try:audit.check_identity(Q(changed['delta']),mappings)
    except ArithmeticError:pass
    else:raise AssertionError('audit accepted mutation')
    tests.append('both reject '+mode)
(BASE/'core/supplementary/checker_adversarial_tests.json').write_text(json.dumps({'status':'PASS','cases':tests},indent=2))
print('Checker review PASS:',len(tests),'cases')
