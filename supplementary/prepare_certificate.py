from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext
import json,hashlib,shutil
BASE=Path(__file__).resolve().parent
CORE=BASE/'core';SUP=CORE/'supplementary'
SEARCH=Path(r'D:/ai4sc/output/gbcp_frontier_20260915')
rows=[]
for log in SEARCH.rglob('witness_*_verified.json'):
    witness=log.with_name(log.name.replace('_verified.json','.json'))
    data=json.loads(log.read_text())
    if data.get('status')!='CERTIFIED' or not witness.exists():continue
    assert hashlib.sha256(witness.read_bytes()).hexdigest()==data['sha256']
    rows.append({'delta':data['delta'],'source':str(witness),'sha256':data['sha256']})
winner=max(rows,key=lambda x:Fraction(x['delta']))
src=Path(winner['source']);raw=json.loads(src.read_text());prior=json.loads(src.with_name(src.stem+'_verified.json').read_text())
delta=Fraction(raw['delta']);baseline=Fraction('0.9808348');assert delta>baseline
payload={'delta':str(delta),'coefficient_order':'ascending powers of s','degrees':{k:len(raw[k]['numerators_ascending'])-1 for k in ('x','y','p')},**{k:raw[k] for k in ('x','y','p')}}
canonical=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
payload_sha=hashlib.sha256(canonical).hexdigest()
intro='''Belgian Chocolate Problem：显式有理多项式证书

全部数组按 s 的升幂排列，且列出全部整数，不使用小数系数。
delta0 = {delta}
deg x = 72; deg y = 72; deg p = 74.

x(s) = (1/D_x) * sum(X_i * s^i, i=0,...,72)
y(s) = (1/D_y) * sum(Y_i * s^i, i=0,...,72)
p(s) = (1/D_p) * sum(P_i * s^i, i=0,...,74)

D_x = D_y = 10^800; D_p = 2000000000000000 * 10^800.
下方 JSON 中各 polynomial 的 denominator 为完整公共分母；
numerators_ascending 为对应完整整数数组 X、Y、P。
恒等式：p(s)=(s^2-2*delta0*s+1)*x(s)+(s^2-1)*y(s)。

CERTIFICATE_PAYLOAD_SHA256 = {payload_sha}
此 SHA-256 对下方 JSON 数学数据按键排序、紧凑 ASCII 编码计算。
本 TXT 文件本身的字节 SHA-256 另列于 SHA256SUMS.txt 和中文说明，
以避免文件包含自身哈希的循环定义。

BEGIN_CERTIFICATE_JSON
'''.format(delta=delta,payload_sha=payload_sha)
txt=CORE/'WITNESS_FINAL.txt'
txt.write_text(intro+json.dumps(payload,ensure_ascii=True,indent=2)+'\nEND_CERTIFICATE_JSON\n',encoding='utf-8',newline='\n')
assert raw['x']['denominator']==raw['y']['denominator']==str(10**800)
assert raw['p']['denominator']==str(2000000000000000*10**800)
with localcontext() as ctx:
    ctx.prec=60
    decimal=str(Decimal(delta.numerator)/Decimal(delta.denominator))
    improvement=delta-baseline
    impdecimal=str(Decimal(improvement.numerator)/Decimal(improvement.denominator))
meta={'delta':str(delta),'decimal':decimal,'previous_public_lower_bound':'0.9808348',
      'improvement':str(improvement),'improvement_decimal':impdecimal,'degrees':payload['degrees'],
      'witness_sha256':hashlib.sha256(txt.read_bytes()).hexdigest(),'payload_sha256':payload_sha,
      'source_sha256':winner['sha256'],'configuration':raw['configuration'],
      'matching_existing_certificates':len(rows),'source':str(src),'selection':'maximum of existing exact-certified witnesses; no new target generated'}
(SUP/'result_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
(SUP/'certificate_selection.json').write_text(json.dumps({'winner':winner,'candidates':sorted(rows,key=lambda x:Fraction(x['delta']))},indent=2))
for name in ('witness_16.json','witness_16_verified.json','interval.json','interval_check.json','quasi.json'):
    shutil.copyfile(src.parent/name,SUP/('source_'+name))
for name in ('literature_check.json','state.json','METHOD.md','parent_growth_fallback_review.json'):
    shutil.copyfile(SEARCH/name,SUP/('project_'+name))
print(json.dumps(meta,indent=2))
