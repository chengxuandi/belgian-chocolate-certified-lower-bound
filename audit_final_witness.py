"""Independent exact Routh-table audit; Python standard library only.
No imports from the primary verifier or from search/production code.
Run: python audit_final_witness.py
"""
import json,hashlib,sys,time
from pathlib import Path
from fractions import Fraction as Rational
from math import gcd

if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

def insist(ok,reason):
    if not ok:raise ArithmeticError(reason)

def load(path):
    lines=path.read_text(encoding='utf-8').splitlines();inside=False;data=[];blocks=0
    for line in lines:
        if line=='BEGIN_CERTIFICATE_JSON':inside=True;blocks+=1
        elif line=='END_CERTIFICATE_JSON':inside=False
        elif inside:data.append(line)
    insist(blocks==1 and not inside,'invalid data block')
    value=json.loads('\n'.join(data))
    insist(value['coefficient_order']=='ascending powers of s','unexpected order')
    polynomials={}
    for name in ['p','y','x']:
        denominator=int(value[name]['denominator']);insist(denominator>0,'invalid denominator')
        values=[int(v) for v in value[name]['numerators_ascending']]
        polynomial={i:Rational(v,denominator) for i,v in enumerate(values) if v!=0}
        insist(polynomial,'zero polynomial')
        insist(max(polynomial)==value['degrees'][name]==len(values)-1,'actual degree mismatch')
        polynomials[name]=polynomial
    return value,Rational(value['delta']),polynomials

def multiply(f,g):
    result={}
    for i,a in f.items():
        for j,b in g.items():result[i+j]=result.get(i+j,Rational(0))+a*b
    return result

def check_identity(delta,polynomials):
    left=multiply({2:Rational(1),1:-2*delta,0:Rational(1)},polynomials['x'])
    right=multiply({2:Rational(1),0:Rational(-1)},polynomials['y'])
    exponents=set(left)|set(right)|set(polynomials['p'])
    insist(all(left.get(i,0)+right.get(i,0)==polynomials['p'].get(i,0) for i in exponents),'identity fails')

def primitive(row):
    divisor=0
    for a in row:divisor=gcd(divisor,a)
    insist(divisor>0,'zero Routh row: strict criterion fails')
    return [a//divisor for a in row]

def routh_test(ascending):
    """Positive primitive integer row scaling avoids Fraction gcd blow-up.
    The ordinary recurrence divides by the positive preceding pivot. Omitting
    that division and dividing by a positive row gcd preserve every row sign.
    Therefore a positive first column here is equivalent to the ordinary table.
    Zero pivots/rows are rejected, never replaced by a numerical epsilon.
    """
    descending=list(reversed(ascending));degree=len(descending)-1
    insist(descending[0]>0,'nonpositive leading coefficient')
    if degree==0:return [descending[0]]
    width=(degree+2)//2
    older=primitive(descending[::2]+[0]*(width-len(descending[::2])))
    newer=primitive(descending[1::2]+[0]*(width-len(descending[1::2])))
    first=[older[0],newer[0]]
    insist(all(v>0 for v in first),'nonpositive initial Routh pivot')
    for _ in range(degree-1):
        row=[newer[0]*older[j+1]-older[0]*newer[j+1] for j in range(width-1)]+[0]
        row=primitive(row);insist(row[0]>0,'nonpositive Routh pivot')
        first.append(row[0]);older,newer=newer,row
    insist(len(first)==degree+1,'incomplete Routh table')
    return first

def main():
    start=time.perf_counter();path=Path(__file__).resolve().parent/'WITNESS_FINAL.txt'
    obj,delta,polynomials=load(path)
    insist(0<delta<1,'parameter outside (0,1)')
    insist(max(polynomials['x'])>=max(polynomials['y']),'degree condition fails')
    print('DEGREE = PASS',flush=True)
    check_identity(delta,polynomials);print('IDENTITY = PASS',flush=True)
    for name in ['p','y','x']:
        column=routh_test([int(v) for v in obj[name]['numerators_ascending']])
        print(name.upper()+'_ROUTH = PASS; positive rows = '+str(len(column)),flush=True)
    print('DELTA = '+str(delta))
    print('WITNESS_SHA256 = '+hashlib.sha256(path.read_bytes()).hexdigest())
    print('SECONDS = '+format(time.perf_counter()-start,'.3f'))
    print('INDEPENDENT_AUDIT = PASS')
    print('FINAL = PASS',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        print('FINAL = FAIL: '+str(error),file=sys.stderr,flush=True);sys.exit(1)
