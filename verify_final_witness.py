"""Standalone exact Hurwitz-matrix verifier. Python standard library only.
Run: python verify_final_witness.py
Input: adjacent WITNESS_FINAL.txt; no search/generator/candidate imports.
Each positive integer pivot below is a complete leading Hurwitz determinant.
"""
from pathlib import Path
from fractions import Fraction
from math import gcd
from functools import reduce
from concurrent.futures import ProcessPoolExecutor
import hashlib,json,sys,time

if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

def require(condition,message):
    if not condition:raise ValueError(message)

def read_certificate(path):
    text=path.read_text(encoding='utf-8')
    require(text.count('BEGIN_CERTIFICATE_JSON')==text.count('END_CERTIFICATE_JSON')==1,'ambiguous certificate block')
    obj=json.loads(text.split('BEGIN_CERTIFICATE_JSON')[1].split('END_CERTIFICATE_JSON')[0])
    require(obj['coefficient_order']=='ascending powers of s','wrong coefficient order')
    return obj

def reconstruct(obj):
    delta=Fraction(obj['delta']);polys={}
    require(0<delta<1,'parameter outside (0,1)')
    for name in ('x','y','p'):
        den=int(obj[name]['denominator']);nums=list(map(int,obj[name]['numerators_ascending']))
        require(den>0 and nums and any(nums),'zero polynomial or invalid denominator')
        degree=max(i for i,a in enumerate(nums) if a)
        require(degree==len(nums)-1==obj['degrees'][name],'actual degree mismatch')
        require(nums[-1]>0,'positive leading coefficient required by this certificate')
        polys[name]=[Fraction(a,den) for a in nums]
    require(len(polys['x'])>=len(polys['y']),'degree x < degree y')
    return delta,polys

def identity(delta,polys):
    def at(name,i):
        return polys[name][i] if 0<=i<len(polys[name]) else Fraction(0)
    for i in range(max(len(polys['p']),len(polys['x'])+2,len(polys['y'])+2)):
        rhs=at('x',i)-2*delta*at('x',i-1)+at('x',i-2)-at('y',i)+at('y',i-2)
        require(at('p',i)==rhs,'nonzero identity coefficient at s^'+str(i))

def hurwitz_minors(nums):
    """Bareiss elimination of the full integer Hurwitz matrix, without swaps.
    Dividing every coefficient by a positive gcd preserves all minor signs.
    The kth pivot equals det(H[:k+1,:k+1]); every division is exact-checked.
    """
    content=reduce(gcd,nums);require(content>0,'zero polynomial')
    a=list(reversed([v//content for v in nums]));n=len(a)-1
    require(a[0]>0,'nonpositive leading coefficient')
    # a[k] is the coefficient of s^(n-k); a[k]=0 outside 0..n.
    H=[[a[2*j-i+1] if 0<=2*j-i+1<=n else 0 for j in range(n)] for i in range(n)]
    previous=1;minors=[]
    for k in range(n):
        pivot=H[k][k];require(pivot>0,'Hurwitz minor '+str(k+1)+' is not strictly positive')
        minors.append(pivot)
        for i in range(k+1,n):
            left=H[i][k]
            for j in range(k+1,n):
                quotient,remainder=divmod(pivot*H[i][j]-left*H[k][j],previous)
                require(remainder==0,'non-exact Bareiss division')
                H[i][j]=quotient
            H[i][k]=0
        previous=pivot
    return minors

def check_one(item):
    name,nums=item
    minors=hurwitz_minors(nums)
    digest=hashlib.sha256(','.join(map(str,minors)).encode('ascii')).hexdigest()
    return name,{'positive_leading_minors':len(minors),'primitive_integer_minors_sha256':digest}

def main():
    started=time.perf_counter();path=Path(__file__).resolve().with_name('WITNESS_FINAL.txt')
    obj=read_certificate(path);delta,polys=reconstruct(obj)
    print('DEGREE = PASS',flush=True)
    identity(delta,polys);print('IDENTITY = PASS',flush=True)
    tasks=[(name,list(map(int,obj[name]['numerators_ascending']))) for name in ('x','y','p')]
    # Three independent polynomial computations; all arithmetic remains exact.
    with ProcessPoolExecutor(max_workers=3) as pool:
        results=dict(pool.map(check_one,tasks))
    for name in ('x','y','p'):print(name.upper()+'_HURWITZ = PASS',flush=True)
    print('DELTA = '+str(delta))
    print('WITNESS_SHA256 = '+hashlib.sha256(path.read_bytes()).hexdigest())
    print('EVIDENCE = '+json.dumps(results,sort_keys=True))
    print('SECONDS = '+format(time.perf_counter()-started,'.3f'))
    print('FINAL = PASS',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        print('FINAL = FAIL: '+str(error),file=sys.stderr,flush=True);sys.exit(1)
