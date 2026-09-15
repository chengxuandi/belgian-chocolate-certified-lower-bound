# AI-Assisted Discovery and Research Provenance

This document describes how an LLM agent was used during discovery of the
certified lower-bound witness in this repository. It is a provenance document,
not part of the mathematical proof. The reported certificate remains

`delta_0 = 1969263222086617/2000000000000000`

with the explicit rational polynomials in `WITNESS_FINAL.txt`.

## 1. Human-specified inputs

The human-specified inputs and acceptance constraints included:

- the strict Belgian Chocolate Problem / generalized polynomial formulation;
- the relevant prior literature, including Charles--Boston's algebraic and
  quasi-admissible configuration framework;
- the requirement to distinguish numerical discovery from an exact theorem;
- the requirement that a certified result use an explicit rational parameter
  and explicit rational polynomials `x`, `y`, and `p`;
- exact verification of the original polynomial identity, actual degrees, and
  strict Hurwitz stability;
- the prohibition on treating floating-point roots, solver status, tolerance,
  or an unverified numerical candidate as proof;
- the requirement for independent verification and an honest public claim.

The human instructions specified the mathematical problem and the proof gate.
They did not specify every search operator, restart policy, numerical fallback,
or implementation optimization described below.

## 2. Prior method and agent-directed discovery

Charles--Boston's algebraic/quasi-admissible framework is prior work. The
agent did not invent that framework. Under the problem definition and exact
acceptance gate, the agent autonomously selected, extended, and navigated the
configuration search. The original contemporaneous record is preserved
verbatim in [`provenance/ORIGINAL_AGENT_METHOD_LOG.md`](provenance/ORIGINAL_AGENT_METHOD_LOG.md).

The attribution table is deliberately conservative. `AGENT-DIRECTED` means the
specific operator or implementation choice is documented as arising during
the agent-run search. `HUMAN-SPECIFIED` means the requirement was already part
of the task or proof gate. `UNCLEAR FROM RECORD` is used whenever the record
does not support a stronger attribution.

| Research action | Attribution | Evidence |
|---|---|---|
| Problem specification and exact acceptance gate | HUMAN-SPECIFIED | task brief; `verify_final_witness.py`; `audit_final_witness.py` |
| Charles--Boston algebraic/quasi-admissible framework | HUMAN-SPECIFIED | prior literature; `REFERENCES.md`; original method log, §1 |
| Growth adjacency operator | AGENT-DIRECTED | original method log, §2; `supplementary/search/frontier_search.py` |
| Balanced split/merge adjacency | AGENT-DIRECTED | original method log, §2; `supplementary/search/frontier_search.py` |
| Origin-growth and lateral moves | AGENT-DIRECTED | original method log, §2; `supplementary/search/origin_backfill.py` |
| Local multi-branch frontier and retained parents | AGENT-DIRECTED | original method log, §2; `supplementary/project_state.json` |
| Complete same-degree adjacency coverage requirement | HUMAN-SPECIFIED | task brief; `provenance/reviews/adjacency_coverage_review.json` |
| Scaled-variable / row-scaled Newton | AGENT-DIRECTED | original method log, §4; `provenance/reviews/fast_mp_review.json` |
| Proposal Jacobian reuse and synthetic-division derivatives | AGENT-DIRECTED | original method log, §4; `provenance/reviews/fast_mp_algebraic_root_identity.json` |
| Direct parent-growth fallback | AGENT-DIRECTED | original method log, §6; `provenance/reviews/parent_growth_fallback_review.json` |
| Stopping-audit correction and failure interpretation | HUMAN-SPECIFIED | task brief's stopping rules; original method log, §6 |
| Adversarial verifier mutation tests | AGENT-DIRECTED | original method log, §5; `provenance/reviews/checker_mutation_results.json` |
| Final theorem acceptance | HUMAN-SPECIFIED | `WITNESS_FINAL.txt`; both verifier scripts and their logs |

The table does not attribute failed numerical branches to mathematical
nonexistence. A failed solve is retained as a diagnostic event only.

## 3. Discovery / proof boundary

Agent search output has no proof status. Numerical continuation, Newton solves,
quasi-admissible roots, interval-isolation candidates, residuals, and search
logs were used to discover and prioritize structures. They are not themselves
the lower-bound theorem.

The only object promoted to the theorem is the saved finite certificate:

```text
delta_0
x(s), y(s), p(s) in Q[s]
p(s) = (s^2 - 2*delta_0*s + 1)x(s) + (s^2 - 1)y(s)
```

`verify_final_witness.py` checks the exact identity, degrees, and integer
Hurwitz determinants. `audit_final_witness.py` independently reconstructs the
identity and checks exact Routh first columns. Neither verifier needs the LLM,
the numerical search, the provenance narrative, or solver status. The theorem
therefore remains checkable without trusting the agent.

## 4. Why the provenance is retained

These records are retained to:

- disclose the concrete role of AI in candidate discovery;
- distinguish prior mathematics, human constraints, and agent research
  decisions;
- let readers reconstruct the discovery history, including failures and
  fallback paths;
- avoid rewriting agent operations after the fact as a human-designed method;
- support reproducibility research on AI-assisted mathematics.

The original method log is intentionally copied without editorial changes.
The curated explanations in this file and in `SEARCH_METHOD_APPENDIX_CN.md`
are separate from that raw record.

## 中文摘要

本项目使用自主 LLM Agent 进行候选发现，但 Agent 不是最终证明的可信
来源。Charles--Boston 的 algebraic/quasi-admissible 框架属于已有文献；
Agent 在其上自主选择并扩展了配置邻接、frontier、origin-growth、缩放
Newton、Jacobian 加速和 parent-growth fallback 等搜索策略。具体归因以
上表和原始记录为准，不能把失败求解当作不存在性证明。

最终 lower bound 只依赖公开的有理数 `delta_0`、`x,y,p` 以及两个独立
exact verifier。只想核验数学结果的读者可以跳过搜索记录，直接运行：

```text
python verify_final_witness.py
python audit_final_witness.py
```
