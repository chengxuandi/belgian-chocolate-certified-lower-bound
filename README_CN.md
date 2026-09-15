# Belgian Chocolate Problem：认证下界材料包

本仓库的核心结果是：

**$\delta=1969263222086617/2000000000000000=0.9846316110433085$ 为 Belgian Chocolate Problem 的一个 certified admissible parameter。**

证书给出非零严格 Hurwitz 多项式 $x,y,p\in\mathbb Q[s]$，次数为 **72、72、74**，满足原始恒等式和 $\deg x\ge\deg y$。
因此 $\delta^*\ge\delta$。与 Charles–Boston 2018 的 $0.9808348$ 相比，精确增量为 **0.0037968110433085**。
截至本项目当前检索，未发现公开结果超过该值；不声称已确定世界纪录或解决完整 GBCP。

## 最快核验方式

```console
python verify_final_witness.py
python audit_final_witness.py
```

Python 3.10+，两套脚本都只依赖标准库，只读取同目录的 `WITNESS_FINAL.txt`。
二者均应输出 `FINAL = PASS`。完整 clean-check 日志及 SHA-256 见 `supplementary/`。
本机纯标准库实测：主 verifier 602.850 秒；独立 audit 93.904 秒。其他机器耗时会不同。
PDF 供阅读、转发和打印；可执行证书及两套脚本负责独立复核。

## 推荐阅读顺序

1. [RESULT_NOTE_CN.md](RESULT_NOTE_CN.md)：1–2 页等效长度的主结果。
2. [FINAL_RESULT_CN.pdf](FINAL_RESULT_CN.pdf)：正式中文说明。
3. [WITNESS_FINAL.txt](WITNESS_FINAL.txt)：完整分母与整数数组。
4. [VERIFICATION_GUIDE_CN.md](VERIFICATION_GUIDE_CN.md)：一页核验指南。
5. [SEARCH_METHOD_APPENDIX_CN.md](SEARCH_METHOD_APPENDIX_CN.md)：仅解释发现过程。

参考文献见 [REFERENCES.md](REFERENCES.md)；PDF 可编辑源文件为 `FINAL_RESULT_CN.tex`。

## 固定证书

- 参数：`1969263222086617/2000000000000000`。
- 次数：`deg x = 72; deg y = 72; deg p = 74`。
- 公共分母：$D_x=D_y=10^{800}$，$D_p=2\times10^{815}$。
- `WITNESS_FINAL.txt` 文件字节 SHA-256：

  `02cce7aa82f7a2d9f15acad837cab2d4be9020b71d7b5998e663da3126625655`

TXT 内另有规范化数学数据的 payload SHA-256；它与整个 TXT 的文件哈希不是同一对象。全部发布文件的字节哈希见 `SHA256SUMS.txt`。

## 整理范围

本轮从现有已通过精确验收的产物中选择最大参数，重写独立核验器并重放证书；没有搜索或生成更大的参数。旧搜索停止于用户要求整理材料的检查点，不据此声称路线已饱和。
`supplementary/` 保存来源、冻结状态、检索记录、完整原始验收数据和本轮复核日志。
