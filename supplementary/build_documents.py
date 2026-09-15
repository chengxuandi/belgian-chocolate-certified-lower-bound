from pathlib import Path
import json
BASE=Path(__file__).resolve().parent;OUT=BASE/'core'
m=json.loads((OUT/'supplementary/result_metadata.json').read_text())
tokens={'DELTA':m['delta'],'DECIMAL':m['decimal'],'IMPROVEMENT':m['improvement'],'IMPDECIMAL':m['improvement_decimal'],'SHA':m['witness_sha256']}
def render(text):
    for k,v in tokens.items():text=text.replace('@@'+k+'@@',v)
    return text.strip()+'\n'
def write(name,text):(OUT/name).write_text(render(text),encoding='utf-8',newline='\n')
write('RESULT_NOTE_CN.md',r'''
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

$$\delta_0=\frac{1969263222086617}{2000000000000000}=@@DECIMAL@@>0.9808348.$$

文件 `WITNESS_FINAL.txt` 明确给出 $x,y,p\in\mathbb Q[s]$，实际次数分别为 **72、72、74**，且它们均非零、严格 Hurwitz，满足

$$\deg x\ge\deg y,\qquad p=(s^2-2\delta_0s+1)x+(s^2-1)y.$$

因此 $\delta_0$ admissible，**$\delta^*\ge\delta_0$**。
相对所引公开基线的精确增量为

$$\delta_0-0.9808348=\frac{7593622086617}{2000000000000000}=@@IMPDECIMAL@@.$$

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

`@@SHA@@`
''')
write('VERIFICATION_GUIDE_CN.md',r'''
# 独立核验指南

**核心结论完全不要求相信搜索算法。** 只需核验最终有限证书 $\delta_0,x,y,p$。
目标参数为 `@@DELTA@@`，即 `@@DECIMAL@@`；多项式实际次数为 $(72,72,74)$。

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

`@@SHA@@`
''')
write('README_CN.md',r'''
# Belgian Chocolate Problem：认证下界材料包

本仓库的核心结果是：

**$\delta=@@DELTA@@=@@DECIMAL@@$ 为 Belgian Chocolate Problem 的一个 certified admissible parameter。**

证书给出非零严格 Hurwitz 多项式 $x,y,p\in\mathbb Q[s]$，次数为 **72、72、74**，满足原始恒等式和 $\deg x\ge\deg y$。
因此 $\delta^*\ge\delta$。与 Charles–Boston 2018 的 $0.9808348$ 相比，精确增量为 **@@IMPDECIMAL@@**。
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

- 参数：`@@DELTA@@`。
- 次数：`deg x = 72; deg y = 72; deg p = 74`。
- 公共分母：$D_x=D_y=10^{800}$，$D_p=2\times10^{815}$。
- `WITNESS_FINAL.txt` 文件字节 SHA-256：

  `@@SHA@@`

TXT 内另有规范化数学数据的 payload SHA-256；它与整个 TXT 的文件哈希不是同一对象。全部发布文件的字节哈希见 `SHA256SUMS.txt`。

## 整理范围

本轮从现有已通过精确验收的产物中选择最大参数，重写独立核验器并重放证书；没有搜索或生成更大的参数。旧搜索停止于用户要求整理材料的检查点，不据此声称路线已饱和。
`supplementary/` 保存来源、冻结状态、检索记录、完整原始验收数据和本轮复核日志。
''')
write('SEARCH_METHOD_APPENDIX_CN.md',r'''
# 搜索方法附录：发现与认证的边界

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

$$\delta_0=@@DELTA@@=@@DECIMAL@@.$$

独立验收重新检查非零、实际次数、原始有理系数恒等式、全部 Hurwitz 顺序主子式及独立 Routh 表。
最终两个独立脚本只读取 `WITNESS_FINAL.txt`，不信任 numerical candidate、求根状态、容差或搜索日志。

**即使搜索过程中存在 numerical error，只要最终 rational witness 独立通过上述精确检查，就不影响该 lower-bound theorem。**

## 6. 本轮范围和来源

现有主搜索已到 degree 72，用户随后要求只整理成果；因此没有继续搜索，也不以该检查点宣称路线饱和。
材料包所用 witness 来自已完成独立验收的救援目录，可能高于冻结主搜索状态中的 incumbent 字段；选择依据是实际 witness 与匹配的精确验收记录，而非该缓存字段。
候选选择清单、原始 witness/验收、冻结状态与搜索日志归档均置于 `supplementary/`。
''')
write('REFERENCES.md',r'''
# 参考文献与检索边界

1. Zachary Charles and Nigel Boston. *Exploiting algebraic structure in global optimization and the Belgian chocolate problem*. Journal of Global Optimization **72**, 241–254 (2018). DOI: [10.1007/s10898-018-0659-5](https://link.springer.com/article/10.1007/s10898-018-0659-5). [arXiv:1708.08114](https://arxiv.org/abs/1708.08114)（预印本发表于 2017 年；正式出版于 2018 年）。本文公开基线 $0.9808348$ 的直接来源。

2. Vincent Blondel. *Simultaneous Stabilization of Linear Systems*. Lecture Notes in Control and Information Sciences, vol. **191**, Springer, 1994. DOI: [10.1007/3-540-19862-8](https://link.springer.com/book/10.1007/3-540-19862-8). 同时稳定化的背景；不作为本证书数值下界的来源。

3. Erwin H. Bareiss. *Sylvester's identity and multistep integer-preserving Gaussian elimination*. Mathematics of Computation **22**(103), 565–578 (1968). DOI: [10.1090/S0025-5718-1968-0226829-0](https://www.ams.org/mcom/1968-22-103/S0025-5718-1968-0226829-0/S0025-5718-1968-0226829-0.pdf). 整数保留消元的算法背景。

## 检索边界

本项目已针对 Belgian Chocolate Problem 的公开论文、arXiv 和正式出版物进行检索，并在本轮重新核对上述主来源。历史检索词及记录见 `supplementary/project_literature_check.json`。

截至本项目当前检索，未发现公开结果超过该值。本句话报告检索发现，不证明文献已被穷尽，也不等同于“世界纪录已经确定”。

本材料中的“Generalized Belgian Chocolate Problem”仅指正文固定的 $a_\delta=s^2-2\delta s+1$、$b=s^2-1$ 与 $\deg x\ge\deg y$ formulation，不扩展到其他同名变体。
''')
write('FINAL_RESULT_CN.tex',r'''
\documentclass[UTF8,a4paper,11pt,fontset=windows]{ctexart}
\usepackage[margin=24mm,top=22mm,bottom=22mm]{geometry}
\usepackage{amsmath,amssymb,booktabs,array,fancyhdr,xcolor,hyperref}
\hypersetup{colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue,pdftitle={Belgian Chocolate Problem 的一个新的认证下界},pdfauthor={}}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.35em}
\linespread{1.12}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Belgian Chocolate Problem：显式有理证书}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\setlength{\headheight}{15pt}
\newcommand{\deltaz}{\frac{1969263222086617}{2000000000000000}}
\newcommand{\file}[1]{\texttt{\detokenize{#1}}}
\newcommand{\pass}{\textsf{PASS}}
\begin{document}
\begin{center}
{\LARGE\bfseries Belgian Chocolate Problem\\[5pt]的一个新的认证下界}\\[9pt]
{\large 显式 Hurwitz 多项式证书与独立精确核验}\\[6pt]
{\small 项目成果中文核验说明}
\end{center}
\section*{摘要}
本文给出参数 $\delta_0=\deltaz=@@DECIMAL@@$ 的显式有限次数有理多项式证书。
该值超过 Charles--Boston 2018 报告的公开下界 $0.9808348$。
两个互不调用的 Python 标准库核验器从同一整数系数文件出发，分别完成 Hurwitz 主子式检查和独立 Routh 表检查。
本结果仅改进 lower bound，不声称解决完整 GBCP。

\section{问题定义}
本文所称 Generalized Belgian Chocolate Problem（GBCP）固定为下述原始多项式 formulation：
\[
 a_\delta(s)=s^2-2\delta s+1,\qquad b(s)=s^2-1.
\]
称 $\delta$ \emph{admissible}，若存在非零实系数多项式 $x(s),y(s),p(s)$，满足
\[
 \deg x\ge\deg y,\qquad p(s)=a_\delta(s)x(s)+b(s)y(s),
\]
且 $x,y,p$ 的每个根 $\lambda$ 均严格满足 $\operatorname{Re}\lambda<0$，即三者均为严格 Hurwitz 多项式。
这里只讨论该 formulation，不引入单位圆约定或其他同名变体。

以 $\delta^*$ 表示可行参数的临界值：$\delta<\delta^*$ 可行，$\delta>\delta^*$ 不可行。
本文只证明一个有限参数可行，从而给出 $\delta^*$ 的下界。

\section{主结果}
\noindent\fbox{\begin{minipage}{0.94\linewidth}
\textbf{定理（显式有理证书）。} 参数
\[
 \delta_0=\deltaz=@@DECIMAL@@
\]
admissible。具体存在 $x,y,p\in\mathbb Q[s]$，实际次数为 $(72,72,74)$，均非零、严格 Hurwitz，并满足原始恒等式及 $\deg x\ge\deg y$。因此
\[
 \boxed{\delta^*\ge\delta_0}.
\]
\end{minipage}}

\noindent 证书为同目录的 \file{WITNESS_FINAL.txt}。定理的证据是该文件中的有限整数数组与下文的精确验收；数值搜索过程不是证明前提。

\newpage
\section{证书摘要与数据约定}
令 $X_i,Y_i,P_i$ 表示证书文件中的完整整数数组，\textbf{均按 $s$ 的升幂排列}：
\begin{align*}
 x(s)&=D_x^{-1}\sum_{i=0}^{72}X_i s^i, & D_x&=10^{800},\\
 y(s)&=D_y^{-1}\sum_{i=0}^{72}Y_i s^i, & D_y&=10^{800},\\
 p(s)&=D_p^{-1}\sum_{i=0}^{74}P_i s^i, & D_p&=2\cdot10^{815}.
\end{align*}
三个数组分别含 73、73、75 个整数。其最高次系数非零且为正，所以实际次数确为 72、72、74，并非仅由数组长度推定。
完整整数过长，不在 PDF 正文重复；\file{WITNESS_FINAL.txt} 已完整列出全部分母和数组，读者不需要运行任何生成脚本才能理解它们。

\begin{center}
\begin{tabular}{lccc}\toprule
 & $x$ & $y$ & $p$\\\midrule
实际次数 & 72 & 72 & 74\\
整数系数个数 & 73 & 73 & 75\\
Hurwitz 顺序主子式数 & 72 & 72 & 74\\
Routh 首列项数 & 73 & 73 & 75\\\bottomrule
\end{tabular}
\end{center}

\subsection*{固定文件的 SHA-256}
\noindent 对 \file{WITNESS_FINAL.txt} 的全部 UTF-8 文件字节计算 SHA-256，得到：
\begin{center}\footnotesize\ttfamily @@SHA@@\end{center}
该文件哈希与 README 及 \file{SHA256SUMS.txt} 一致。TXT 内另列有规范化数学数据的 payload 哈希；它校验 JSON 数学数据，与整个 TXT 的文件字节哈希是两个不同对象。

\subsection*{定理如何从证书得到}
第一步，将分母和整数数组重建为 $\mathbb Q[s]$ 中的三个多项式；第二步，逐系数检查
\[
 p-(s^2-2\delta_0s+1)x-(s^2-1)y=0;
\]
第三步，检查次数条件和三个多项式的严格 Hurwitz 性。全部条件成立后，直接应用第 1 节定义即可推出 admissibility，进而得到 $\delta^*\ge\delta_0$。

该推论不需要断言搜索穷尽了全部配置，也不需要判断任何浮点根的实部是否接近零。本文没有为了扩大结论再生成或验证一个更大的参数。

\newpage
\section{精确核验}
对实多项式 $f(s)=a_0s^n+a_1s^{n-1}+\cdots+a_n$，$a_0>0$，定义
\[
 H(f)_{ij}=a_{2j-i}\quad(1\le i,j\le n),\qquad
 a_k=0\ \text{若 }k\notin\{0,\ldots,n\}.
\]
按 Routh--Hurwitz 判据，$f$ 严格 Hurwitz 当且仅当所有顺序主子式
\[
 \Delta_k(f)=\det H(f)_{1:k,1:k}>0,\qquad k=1,\ldots,n.
\]
主核验器 \file{verify_final_witness.py} 显式构造三个完整 Hurwitz 矩阵，使用 Bareiss 整数消元\cite{bareiss}计算全部所需主子式。每次整除都检查余数为零。约去系数的正公共因子只对第 $k$ 个主子式作正比例缩放，故不改变判据。

\begin{center}
\begin{tabular}{p{0.67\linewidth}c}\toprule
核验项目 & 结果\\\midrule
原始多项式恒等式（精确有理系数） & \pass\\
非零、实际次数与 $\deg x\ge\deg y$ & \pass\\
$x$：全部 72 个 Hurwitz 顺序主子式严格为正 & \pass\\
$y$：全部 72 个 Hurwitz 顺序主子式严格为正 & \pass\\
$p$：全部 74 个 Hurwitz 顺序主子式严格为正 & \pass\\
独立 exact Routh table（共 221 个首列项） & \pass\\\bottomrule
\end{tabular}
\end{center}

第二核验器 \file{audit_final_witness.py} 不调用主程序。它独立解析文件，用稀疏多项式乘法检查恒等式，再构造 Routh 表。为避免有理分数膨胀，每行仅做正整数比例缩放；这不改变首列符号。零行或零枢轴直接拒绝，绝不以数值 epsilon 替代。

\section{如何复核}
在解压后的材料目录，使用 Python 3.10 或更新版本执行：
\begin{quote}\ttfamily
python verify\_final\_witness.py\\
python audit\_final\_witness.py
\end{quote}
两者均只依赖 Python 标准库，只读取同目录的 \file{WITNESS_FINAL.txt}；不导入搜索代码、生成代码、数值候选或第三方 CAS。两条命令均应以 \file{FINAL = PASS} 结束。

本轮已将三个文件复制到干净目录，以 \file{python -I -S} 重放，隔离外部模块路径并禁用 site 初始化。完整输出、针对性反例检查与验收元数据保存于 \file{supplementary/}。本机主核验耗时约 603 秒，独立审计约 94 秒；其他机器耗时会不同。

\newpage
\section{与已有结果的关系}
Charles--Boston 的正式论文发表于 2018 年，报告 $0.9808348$ admissible\cite{cb}。本证书给出更大的可行参数：
\begin{align*}
 \delta_0&=\deltaz=@@DECIMAL@@,\\
 \delta_0-0.9808348
 &=\frac{7593622086617}{2000000000000000}\\
 &=@@IMPDECIMAL@@>0.
\end{align*}
\textbf{截至本项目当前检索，未发现公开结果超过该值。}
这是一项有边界的文献检索陈述，不等于已确定世界纪录。本文不声称全局最优，也不确定 $\delta^*$ 的精确位置；同时稳定化的背景可参见 Blondel\cite{blondel}。

\section{发现方法与证明的区别}
候选来自 algebraic/quasi-admissible configuration 的增长与多初值数值求根。随后通过严格区间隔离、从 quasi 到 strict stable 的变换，以及系数有理化形成最终候选。
这些步骤解释\emph{证书如何被发现}；最终正确性则由实际保存的 $\delta_0,x,y,p$ 及两套独立整数／有理数核验建立。

\begin{center}
\textbf{numerical search = discovery}\qquad
\textbf{exact rational witness = proof}
\end{center}
即使发现过程中存在数值误差，只要最终有限证书独立通过精确验收，本下界定理仍然成立。
详细方法放在 \file{SEARCH_METHOD_APPENDIX_CN.md}，不混入主证明。
本轮只整理和复核已有最好证书，没有继续推进参数，也不将用户要求停止搜索的检查点解释为路线饱和。

\begin{thebibliography}{9}\small
\bibitem{cb} Z. Charles and N. Boston.
Exploiting algebraic structure in global optimization and the Belgian chocolate problem.
\emph{Journal of Global Optimization}, 72:241--254, 2018.
\href{https://doi.org/10.1007/s10898-018-0659-5}{doi:10.1007/s10898-018-0659-5}.
\bibitem{blondel} V. Blondel.
\emph{Simultaneous Stabilization of Linear Systems}.
Lecture Notes in Control and Information Sciences 191, Springer, 1994.
\href{https://doi.org/10.1007/3-540-19862-8}{doi:10.1007/3-540-19862-8}.
\bibitem{bareiss} E. H. Bareiss.
Sylvester's identity and multistep integer-preserving Gaussian elimination.
\emph{Mathematics of Computation}, 22(103):565--578, 1968.
\href{https://doi.org/10.1090/S0025-5718-1968-0226829-0}{doi:10.1090/S0025-5718-1968-0226829-0}.
\end{thebibliography}
\end{document}
''')
print('Chinese Markdown documents and editable LaTeX source created')
