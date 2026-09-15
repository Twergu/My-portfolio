# Verification mode comparison

Dataset: policy-challenge-v2.1; split: test; chunk size/overlap: 900/0; query workers: 2.

Generator and verifier: gpt-5.6-luna / gpt-5.6-luna; independent Judge: gpt-4.1.

| Mode | Correctness | Citation groundedness | Refusal accuracy | Quote mismatch | Unsupported | False refusal | Query p50 ms | Query p95 ms | Mean query USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| off | 0.97619048 | 1.00000000 | 0.98148148 | 0.00000000 | 0.00000000 | 0.02380952 | 3527.50535001 | 6822.62708500 | 0.00057060 |
| fast | 0.92857143 | 1.00000000 | 0.98148148 | 0.00000000 | 0.00000000 | 0.02380952 | 3389.12990000 | 6984.66103500 | 0.00056931 |
| strict | 0.83333333 | 1.00000000 | 0.85185185 | 0.00000000 | 0.05555556 | 0.16666667 | 5426.14704999 | 9751.65452000 | 0.00081014 |

Citation groundedness is an independent evaluation of delivered answers; it is not the runtime verifier pass rate. Off/fast remain semantically unverified in the application. Correctness uses answerable questions; refusal accuracy uses all questions. See each mode JSON for denominators and rejected-candidate diagnostics.

Query latency/cost excludes the extra evaluation Judge and indexing. One generation per question/mode; generation randomness remains a confounder, so this is a pipeline comparison, not a paired replay of identical candidate answers. Test scores are reported without tuning prompts on test failures.
