# Diagnostic baseline — superseded evaluation protocol

This first real 54-question development run used a single Judge prompt containing both gold evidence and actual citations. Inspection found explanations that borrowed uncited gold evidence when assessing citation support. Its citation-groundedness and false-rejection estimates must not be treated as the final quality results.

The original report is retained unchanged for traceability and incurred cost accounting. No test questions were used to revise the evaluator. The replacement protocol is `isolated-correctness-and-citations-v2`: correctness sees the reference, while a separate citation judge sees only the question and the candidate's actual cited sources. Generator instructions also explicitly require contiguous quotes and all premises for cross-document claims.

Final results belong in `reports/chunks-api/` and `reports/verification/`. The baseline is not reused for parameter selection under the new protocol.
