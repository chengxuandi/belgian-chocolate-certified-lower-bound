# 搜索方法附录：发现与认证的边界

> 本文档是搜索方法的整理版。Agent 的原始方法记录和运行中具体策略
> 变化请见：`provenance/ORIGINAL_AGENT_METHOD_LOG.md`。
>
> 人类整理的 Agent 使用说明见：`AGENT_PROVENANCE.md`。

搜索方法用于发现候选，不构成最终 lower-bound theorem 的证明；最终结论
只由保存的有理数 witness 和两个独立 exact verifier 建立。

本附录解释结果如何找到，**不是主定理的证明前提**。核心证明仅由最终 $\mathbb Q[s]$ 证书及独立精确验收组成。

## 1. 基线与 algebraic specification

Charles–Boston 2018 报告 $0.9808348$ admissible，并使用 quasi-admissible algebraic configuration。令 $t=s^2$，以整数重数向量 $j,k,\ell$ 和正因子参数表示

$$X(t)=\prod_i(t+A_i)^{j_i},\quad Y(t)=g\prod_i(t+B_i)^{k_i},\quad Z(t)=t^h\prod_i(t+C_i)^{\ell_i}.$$

求解整数系数多项式方程

$$[t^2+(2-4d^2)t+1]X(t)+(t-1)Y(t)-Z(t)=0.$$

这给出边界形式 $x_d=(s^2+2ds+1)X(s^2)$、$y_d=Y(s^2)$、$p_d=Z(s^2)$。它们可能在虚轴上有根，不能直接作为 strict stable 证书。

## 2. Discovery：配置增长与数值求解

从已知 degree-22 分支向 degree 24、26 等增长，尝试增加重数、增加频率、平衡拆分/合并及调整原点重数；对标签排列去重，并保留多个分支。
数值阶段使用解析 Jacobian、多初值和高精度 Newton。最终选定证书来自 degree-72 配置：

```text
j = [11,4,3,2,2,2,2,2,2,2,1,1,1]
k = [6,3,3,2,2,2,2,2,2,2,2,1,1,1]
ell = [5,3,2,2,2,1,1,1]
h = 20 (p_d 中原点重数为 40)
```

该分支先前从浮点解细化失败，随后从已认证父配置的增长初值直接做高精度求解成功。该事实仅描述发现过程，不是稳定性证据。

## 3. Quasi 解的严格隔离

用有理中心、dyadic 隔离盒和有理近似逆矩阵构造收缩映射。向外舍入的整数区间运算验证映射严格进入盒内部、收缩常数小于 1、Jacobian 非奇异和所有因子参数正性，得到唯一代数解的严格隔离证书。
相关来源文件保存在 `supplementary/source_interval.json` 与 `source_interval_check.json`。这些文件有助于复核发现链条，但独立主 verifier 不读取它们。

## 4. 从 quasi 到 strict stable，再有理化

对严格小于已隔离 quasi 参数的有理目标，使用已验证的 Möbius 变换将边界根移到左半平面，再有理化 $x,y$ 的系数。随后按目标参数的原始恒等式精确定义 $p$。
变换和有理化的数值输出仍不能独自证明结论，必须重新对实际得到的三个有理多项式验收。

## 5. Certification：最终有限证书

本材料固定使用已经精确验收的

$$\delta_0=1969263222086617/2000000000000000=0.9846316110433085.$$

独立验收重新检查非零、实际次数、原始有理系数恒等式、全部 Hurwitz 顺序主子式及独立 Routh 表。
最终两个独立脚本只读取 `WITNESS_FINAL.txt`，不信任 numerical candidate、求根状态、容差或搜索日志。

**即使搜索过程中存在 numerical error，只要最终 rational witness 独立通过上述精确检查，就不影响该 lower-bound theorem。**

## 6. 本轮范围和来源

现有主搜索已到 degree 72，用户随后要求只整理成果；因此没有继续搜索，也不以该检查点宣称路线饱和。
材料包所用 witness 来自已完成独立验收的救援目录，可能高于冻结主搜索状态中的 incumbent 字段；选择依据是实际 witness 与匹配的精确验收记录，而非该缓存字段。
候选选择清单、原始 witness/验收、冻结状态与搜索日志归档均置于 `supplementary/`。
