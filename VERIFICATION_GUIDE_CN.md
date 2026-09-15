# 独立核验指南

**核心结论完全不要求相信搜索算法。** 只需核验最终有限证书 $\delta_0,x,y,p$。
目标参数为 `1969263222086617/2000000000000000`，即 `0.9846316110433085`；多项式实际次数为 $(72,72,74)$。

## A. 恒等式

`WITNESS_FINAL.txt` 列出公共分母和完整整数数组，按 $s$ 的升幂排列。
主 verifier 用 Python `Fraction` 逐项检查 $p-(s^2-2\delta_0s+1)x-(s^2-1)y$ 的系数全为零。

## B. 次数条件

从非零整数系数重新计算 actual degree，检查非零、正首项、$(72,72,74)$ 与 $\deg x\ge\deg y$。
不以数组长度或标注次数替代非零首项检查。

## C. 严格 Hurwitz 性

主 verifier 对三个完整 Hurwitz 矩阵做无浮点的 Bareiss 整数消元；每次整除检查余数为零，全部 218 个顺序主子式严格为正。
以正公共因子约去整数系数的内容只改变主子式的正比例因子，不改变根或符号。

## D. 第二套独立验收

`audit_final_witness.py` 独立解析证书，以稀疏多项式乘法检查恒等式，再用 exact Routh table 检查全部 221 个首列项。
每行只做正整数比例缩放；零行、零枢轴直接拒绝，不使用 epsilon。
两套脚本互不调用，且不导入搜索或生成程序。

```console
python verify_final_witness.py
python audit_final_witness.py
```

需要 Python 3.10+，不需要安装第三方包。本机主核验约 603 秒，独立 Routh 约 94 秒；其他机器耗时会不同。主程序并行检查三个多项式。干净目录实测日志见 `supplementary/`。

**numerical optimization 只用于发现候选，不进入最终正确性证明。**
本证书证明 $\delta_0$ admissible，故 $\delta^*\ge\delta_0$；不证明临界值的精确位置。

文件字节 SHA-256（`WITNESS_FINAL.txt`）：

`02cce7aa82f7a2d9f15acad837cab2d4be9020b71d7b5998e663da3126625655`
