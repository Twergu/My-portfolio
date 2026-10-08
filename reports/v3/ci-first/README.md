# First v3 CI snapshot

Original artifact bytes from [CI run 35039880066](https://github.com/Twergu/My-portfolio/actions/runs/35039880066), tested application commit `07ae4e8419daf9e32b19146895fe113d8f332264`. The final code run is linked from `reports/ci-status.json`; its measured vectors are in `reports/vector-scale.json`.

Both runs passed the zero-skip test gate. HNSW index construction and shared CI hardware vary: at 10k chunks, ef=400 recall was 0.95 then 0.91; at 100k, ef=1000 recall was 0.57 then 0.67. These results do not establish a stable production threshold. Exact remains the default and each deployment must evaluate its own filtered corpus.
