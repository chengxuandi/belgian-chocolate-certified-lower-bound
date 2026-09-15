# Belgian Chocolate Problem 的一个新的认证下界

## 1. 问题

令 $a_\delta(s)=s^2-2\delta s+1$、$b(s)=s^2-1$。
参数 $\delta$ admissible，指存在非零实系数多项式 $x,y,p$，
满足 $\deg x\ge\deg y$ 与 $p=a_\delta x+by$，
且三个多项式的所有根均严格满足 $\operatorname{Re}\lambda<0$。
本文只使用上述原始多项式 formulation。

## 2. 已知背景

- 已知存在临界值 $\delta^*$：$\delta<\delta^*$ 可行，$\delta>\delta^*$ 不可行。
- Charles–Boston 2018 给出的公开 lower bound 为 $0.9808348$。[正式论文](https://link.springer.com/article/10.1007/s10898-018-0659-5)
- 本结果只改进 lower bound，不声称解决完整 GBCP。

## 3. 新结果

**定理。** 令

$$\delta_0=\frac{1969263222086617}{2000000000000000}=0.9846316110433085>0.9808348.$$

文件 `WITNESS_FINAL.txt` 明确给出 $x,y,p\in\mathbb Q[s]$，实际次数分别为 **72、72、74**，且它们均非零、严格 Hurwitz，满足

$$\deg x\ge\deg y,\qquad p=(s^2-2\delta_0s+1)x+(s^2-1)y.$$

因此 $\delta_0$ admissible，**$\delta^*\ge\delta_0$**。
相对所引公开基线的精确增量为

$$\delta_0-0.9808348=\frac{7593622086617}{2000000000000000}=0.0037968110433085.$$

截至本项目当前检索，未发现公开结果超过该值。此表述不等于已确定世界纪录，也不构成全局最优性结论。

## 4. 核验方法

- 原始多项式恒等式逐系数通过 exact rational arithmetic。
- 主 verifier 构造 Hurwitz 矩阵并精确计算全部 218 个所需顺序主子式，均严格为正。
- 第二 checker 独立构造 exact Routh table，221 个首列项均严格为正；它不调用主 verifier。
- 全过程不依赖 floating-point roots、数值容差或搜索程序的成功状态。

## 5. 复现

在材料目录执行（Python 3.10+，仅标准库）：

```console
python verify_final_witness.py
```

独立复核可再运行 `python audit_final_witness.py`。二者均应以 `FINAL = PASS` 结束。

`WITNESS_FINAL.txt` 的文件字节 SHA-256：

`02cce7aa82f7a2d9f15acad837cab2d4be9020b71d7b5998e663da3126625655`
