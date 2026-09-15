# 补充材料

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
