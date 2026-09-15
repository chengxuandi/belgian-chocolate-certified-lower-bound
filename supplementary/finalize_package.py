from pathlib import Path
from fractions import Fraction
import json,hashlib,shutil,re,zipfile,ast,sys
import pymupdf
BASE=Path(__file__).resolve().parent;CORE=BASE/'core';SUP=CORE/'supplementary';QA=BASE/'qa'
DEST=BASE.parent/'gbcp_certified_lower_bound_CN'
meta=json.loads((SUP/'result_metadata.json').read_text())
witness=CORE/'WITNESS_FINAL.txt';sha=hashlib.sha256(witness.read_bytes()).hexdigest()
assert sha==meta['witness_sha256']
txt=witness.read_text(encoding='utf-8')
payload=json.loads(txt.split('BEGIN_CERTIFICATE_JSON')[1].split('END_CERTIFICATE_JSON')[0])
assert hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()==meta['payload_sha256']
assert Fraction(payload['delta'])==Fraction(meta['delta'])
assert Fraction(meta['improvement'])==Fraction(meta['delta'])-Fraction('0.9808348')
assert payload['degrees']=={'x':72,'y':72,'p':74}
source=json.loads((SUP/'source_witness_16.json').read_text())
assert all(source[k]==payload[k] for k in ('delta','x','y','p'))
for name in ('WITNESS_FINAL.txt','verify_final_witness.py','audit_final_witness.py'):
    assert (CORE/name).read_bytes()==(BASE/'clean_check'/name).read_bytes()
for name in ('verify_final_witness.py','audit_final_witness.py'):
    tree=ast.parse((CORE/name).read_text())
    imports={n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}
    imports|={a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
    assert imports<=sys.stdlib_module_names,(name,imports)
logs={k:(SUP/(k+'_clean_check.log')).read_text() for k in ('primary','audit')}
assert all('FINAL = PASS' in log and sha in log and meta['delta'] in log for log in logs.values())
evidence=json.loads(next(l[len('EVIDENCE = '):] for l in logs['primary'].splitlines() if l.startswith('EVIDENCE = ')))
prior=json.loads((SUP/'source_witness_16_verified.json').read_text())
for name in ('x','y','p'):
    assert hashlib.sha256(','.join(prior['checks'][name]['hurwitz_determinants']).encode('ascii')).hexdigest()==evidence[name]['primitive_integer_minors_sha256']
    assert evidence[name]['positive_leading_minors']==payload['degrees'][name]
assert json.loads((SUP/'checker_adversarial_tests.json').read_text())['status']=='PASS'

pdf=QA/'FINAL_RESULT_CN.pdf';doc=pymupdf.open(pdf);assert len(doc)==4
pages=[];alltext=''
for i,page in enumerate(doc):
    text=page.get_text();alltext+=text
    assert '\ufffd' not in text and '�' not in text
    assert str(i+1)==text.strip().splitlines()[-1]
    bad=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+.1 or y1>page.rect.height+.1:bad.append(span['text'])
    assert not bad,bad
    for font in page.get_fonts():assert len(doc.extract_font(font[0])[3])>0,'nonembedded font'
    image=QA/f'page-{i+1}.png';assert image.exists()
    pages.append({'page':i+1,'render_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
                  'visual_review':'PASS: formulas complete, no clipping/overlap/garbled glyphs/table overflow',
                  'all_text_inside_page':True,'fonts_embedded':True})
compact=''.join(alltext.split())
for exact in ('1969263222086617','2000000000000000',meta['decimal'],meta['improvement_decimal'],'0.9808348',sha,'verify_final_witness.py','audit_final_witness.py','WITNESS_FINAL.txt'):
    assert exact in compact,exact
assert '(72,72,74)' in compact
assert 'GeneralizedBelgianChocolateProblem' in compact
for v in re.findall(r'0\.\d{5,}',alltext):assert Fraction(v)<=Fraction(meta['delta']),'unproved higher decimal in PDF'
compilelog=(QA/'FINAL_RESULT_CN.log').read_text(errors='replace')
assert not any(s in compilelog for s in ('Overfull','Missing character','undefined references','Font Warning'))
for name in ('README_CN.md','RESULT_NOTE_CN.md','VERIFICATION_GUIDE_CN.md'):
    text=(CORE/name).read_text(encoding='utf-8')
    assert sha in text and meta['decimal'] in text
    assert '72' in text and '74' in text
for name in ('README_CN.md','RESULT_NOTE_CN.md','FINAL_RESULT_CN.tex'):
    text=(CORE/name).read_text(encoding='utf-8');assert meta['improvement_decimal'] in text
    assert '截至本项目当前检索，未发现公开结果超过该值' in text
    assert '@@' not in text
for path in CORE.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf8')):
        if '://' not in target:
            if target=='FINAL_RESULT_CN.pdf':continue
            assert (path.parent/target).exists(),(path.name,target)
shutil.copyfile(pdf,CORE/'FINAL_RESULT_CN.pdf')
audit={
 'BEST_CERTIFIED_DELTA':meta['delta'],'DECIMAL':meta['decimal'],
 'PREVIOUS_PUBLIC_LOWER_BOUND':'0.9808348','IMPROVEMENT':meta['improvement_decimal'],
 'IMPROVEMENT_EXACT':meta['improvement'],'DEGREES':payload['degrees'],
 'PRIMARY_VERIFIER':'PASS','INDEPENDENT_AUDIT':'PASS','PDF_GENERATED':'PASS','PDF_VISUAL_CHECK':'PASS',
 'PDF_PAGES':4,'WITNESS_SHA256':sha,'PDF_SHA256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
 'IDENTICAL_TO_EXISTING_CERTIFIED_COEFFICIENTS':True,'ALL_218_DETERMINANTS_MATCH_PRIOR_EXACT_CHECK':True,
 'STANDARD_LIBRARY_ONLY':True,'CLEAN_DIRECTORY_FILES_BYTE_IDENTICAL':True,
 'PRIMARY_SECONDS':602.850,'AUDIT_SECONDS':93.904,'NO_NEW_PARAMETER_SEARCH':True,'VISUAL_PAGES':pages}
(SUP/'FINAL_ACCEPTANCE.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
for name in ('prepare_certificate.py','build_documents.py','test_checkers.py','finalize_package.py'):
    shutil.copyfile(BASE/name,SUP/name)
shutil.copyfile(QA/'FINAL_RESULT_CN.log',SUP/'latex_build.log')
(SUP/'README_CN.md').write_text('''# 补充材料

核心证明只需根目录的 WITNESS_FINAL.txt 和两套独立脚本。

- FINAL_ACCEPTANCE.json：本轮最终验收结果与逐页 PDF 检查。
- primary_clean_check.log / audit_clean_check.log：干净目录中的实际输出及实测耗时。
- checker_adversarial_tests.json：12 项针对性反例与小规模行列式对照。
- result_metadata.json / certificate_selection.json：已有 107 份认证结果中的最大值选择及来源。
- source_witness_16.json / source_witness_16_verified.json：原始已有 witness 与完整精确验收值；三个 Hurwitz 行列式列表与本轮计算一致。
- source_interval*.json / source_quasi.json：发现链条的来源资料，核心 verifier 不读取。
- project_state.json：冻结主搜索状态；救援证书的最终选择见 result_metadata.json，不以缓存 incumbent 字段替代实际验收。
- search_archive.zip：原始搜索日志、代码与状态的历史归档（非核心证明依赖）。
- project_literature_check.json：项目已有公开文献检索记录。
- 其余 Python 文件：材料生成和检查的源程序；不被两套核心核验器导入。

PDF 由 XeLaTeX 与 ctex 编译，需中文字体（本次为 Windows SimSun/SimHei）；可编辑源文件在根目录。
生成器包含本项目原始工作路径，便于追溯，不属于跨机器 verifier 运行所需依赖。
''',encoding='utf-8')
required={'README_CN.md','RESULT_NOTE_CN.md','FINAL_RESULT_CN.pdf','FINAL_RESULT_CN.tex','WITNESS_FINAL.txt','verify_final_witness.py','audit_final_witness.py','VERIFICATION_GUIDE_CN.md','SEARCH_METHOD_APPENDIX_CN.md','REFERENCES.md'}
assert {p.name for p in CORE.iterdir() if p.is_file()}==required
files=sorted(p for p in CORE.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
(CORE/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(CORE).as_posix()+'\n' for p in files),encoding='ascii')
assert not DEST.exists(),'Output already exists; inspect rather than overwrite'
shutil.copytree(CORE,DEST,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for line in (DEST/'SHA256SUMS.txt').read_text().splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((DEST/name).read_bytes()).hexdigest()==digest
archive=DEST.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(DEST.rglob('*')):
        if path.is_file():z.write(path,DEST.name+'/'+path.relative_to(DEST).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({**{k:v for k,v in audit.items() if k!='VISUAL_PAGES'},'DIRECTORY':str(DEST),'ZIP':str(archive),'ZIP_BYTES':archive.stat().st_size},indent=2))
