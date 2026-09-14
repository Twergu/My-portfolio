# Knowbase 源码目录

所有链接相对于项目根目录，复制、克隆或解压到其他位置后仍可使用。

目录由 `python -m scripts.source_index` 从当前文件生成；`dist/` 就是可直接修改的 HTML、JavaScript、CSS 源文件，无需额外构建。

需要完整压缩包时运行 `python -m scripts.source_index --archive`，输出 `exports/knowbase-source-latest.zip`。

## 说明、配置与启动

- [.dockerignore](.dockerignore)
- [.env.example](.env.example)
- [.gitattributes](.gitattributes)
- [.gitignore](.gitignore)
- [compose.yaml](compose.yaml)
- [Dockerfile](Dockerfile)
- [pytest.ini](pytest.ini)
- [README.md](README.md)
- [requirements-dev.txt](requirements-dev.txt)
- [requirements-lock.txt](requirements-lock.txt)
- [requirements.txt](requirements.txt)
- [run.py](run.py)
- [SOURCE_INDEX.md](SOURCE_INDEX.md)
- [start.ps1](start.ps1)

## 前端

- [dist/app.js](dist/app.js)
- [dist/favicon.svg](dist/favicon.svg)
- [dist/index.html](dist/index.html)
- [dist/styles.css](dist/styles.css)

## 后端

- [backend/__init__.py](backend/__init__.py)
- [backend/config.py](backend/config.py)
- [backend/main.py](backend/main.py)
- [backend/parse_pdf.py](backend/parse_pdf.py)
- [backend/postgres_store.py](backend/postgres_store.py)
- [backend/providers.py](backend/providers.py)
- [backend/rag.py](backend/rag.py)
- [backend/store.py](backend/store.py)
- [backend/telemetry.py](backend/telemetry.py)

## 测试

- [tests/conftest.py](tests/conftest.py)
- [tests/test_challenge.py](tests/test_challenge.py)
- [tests/test_evaluation.py](tests/test_evaluation.py)
- [tests/test_grounding.py](tests/test_grounding.py)
- [tests/test_observability.py](tests/test_observability.py)
- [tests/test_pipeline.py](tests/test_pipeline.py)
- [tests/test_providers.py](tests/test_providers.py)
- [tests/test_stores.py](tests/test_stores.py)

## 评估数据与协议

- [evals/__init__.py](evals/__init__.py)
- [evals/dataset.json](evals/dataset.json)
- [evals/hard_dataset.json](evals/hard_dataset.json)
- [evals/judge.py](evals/judge.py)
- [evals/make_hard.py](evals/make_hard.py)
- [evals/make_seed.py](evals/make_seed.py)
- [evals/metrics.py](evals/metrics.py)
- [evals/README.md](evals/README.md)

## 运行与实验脚本

- [scripts/benchmark_scale.py](scripts/benchmark_scale.py)
- [scripts/benchmark_stores.py](scripts/benchmark_stores.py)
- [scripts/check.py](scripts/check.py)
- [scripts/chunk_experiment.py](scripts/chunk_experiment.py)
- [scripts/container_smoke.py](scripts/container_smoke.py)
- [scripts/evaluate.py](scripts/evaluate.py)
- [scripts/init_database_password.py](scripts/init_database_password.py)
- [scripts/live_smoke.py](scripts/live_smoke.py)
- [scripts/migrate_sqlite.py](scripts/migrate_sqlite.py)
- [scripts/results_summary.py](scripts/results_summary.py)
- [scripts/source_index.py](scripts/source_index.py)
- [scripts/verification_experiment.py](scripts/verification_experiment.py)

## 架构与修改说明

- [docs/adr/0001-physical-page-chunks.md](docs/adr/0001-physical-page-chunks.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/change-report.md](docs/change-report.md)
- [docs/optimization-report.md](docs/optimization-report.md)

## 示例 PDF

- [samples/employee-handbook.pdf](samples/employee-handbook.pdf)

## 持续集成

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

## 实际运行报告

报告包含运行时间与验证范围，blocked/skipped 表示尚未实测或未执行。

- [reports/chunks/chunk-experiment-local.json](reports/chunks/chunk-experiment-local.json)
- [reports/chunks/chunk-experiment-local.md](reports/chunks/chunk-experiment-local.md)
- [reports/chunks/chunk-local-1200-120-dev.json](reports/chunks/chunk-local-1200-120-dev.json)
- [reports/chunks/chunk-local-1200-120-dev.md](reports/chunks/chunk-local-1200-120-dev.md)
- [reports/chunks/chunk-local-1200-180-dev.json](reports/chunks/chunk-local-1200-180-dev.json)
- [reports/chunks/chunk-local-1200-180-dev.md](reports/chunks/chunk-local-1200-180-dev.md)
- [reports/chunks/chunk-local-450-0-dev.json](reports/chunks/chunk-local-450-0-dev.json)
- [reports/chunks/chunk-local-450-0-dev.md](reports/chunks/chunk-local-450-0-dev.md)
- [reports/chunks/chunk-local-450-60-dev.json](reports/chunks/chunk-local-450-60-dev.json)
- [reports/chunks/chunk-local-450-60-dev.md](reports/chunks/chunk-local-450-60-dev.md)
- [reports/chunks/chunk-local-900-0-dev.json](reports/chunks/chunk-local-900-0-dev.json)
- [reports/chunks/chunk-local-900-0-dev.md](reports/chunks/chunk-local-900-0-dev.md)
- [reports/chunks/chunk-local-900-120-dev.json](reports/chunks/chunk-local-900-120-dev.json)
- [reports/chunks/chunk-local-900-120-dev.md](reports/chunks/chunk-local-900-120-dev.md)
- [reports/chunks/chunk-local-selected-test.json](reports/chunks/chunk-local-selected-test.json)
- [reports/chunks/chunk-local-selected-test.md](reports/chunks/chunk-local-selected-test.md)
- [reports/chunks-v2/chunk-experiment-local.json](reports/chunks-v2/chunk-experiment-local.json)
- [reports/chunks-v2/chunk-experiment-local.md](reports/chunks-v2/chunk-experiment-local.md)
- [reports/chunks-v2/chunk-local-1200-120-dev.json](reports/chunks-v2/chunk-local-1200-120-dev.json)
- [reports/chunks-v2/chunk-local-1200-120-dev.md](reports/chunks-v2/chunk-local-1200-120-dev.md)
- [reports/chunks-v2/chunk-local-1200-180-dev.json](reports/chunks-v2/chunk-local-1200-180-dev.json)
- [reports/chunks-v2/chunk-local-1200-180-dev.md](reports/chunks-v2/chunk-local-1200-180-dev.md)
- [reports/chunks-v2/chunk-local-450-0-dev.json](reports/chunks-v2/chunk-local-450-0-dev.json)
- [reports/chunks-v2/chunk-local-450-0-dev.md](reports/chunks-v2/chunk-local-450-0-dev.md)
- [reports/chunks-v2/chunk-local-450-60-dev.json](reports/chunks-v2/chunk-local-450-60-dev.json)
- [reports/chunks-v2/chunk-local-450-60-dev.md](reports/chunks-v2/chunk-local-450-60-dev.md)
- [reports/chunks-v2/chunk-local-900-0-dev.json](reports/chunks-v2/chunk-local-900-0-dev.json)
- [reports/chunks-v2/chunk-local-900-0-dev.md](reports/chunks-v2/chunk-local-900-0-dev.md)
- [reports/chunks-v2/chunk-local-900-120-dev.json](reports/chunks-v2/chunk-local-900-120-dev.json)
- [reports/chunks-v2/chunk-local-900-120-dev.md](reports/chunks-v2/chunk-local-900-120-dev.md)
- [reports/chunks-v2/chunk-local-selected-test.json](reports/chunks-v2/chunk-local-selected-test.json)
- [reports/chunks-v2/chunk-local-selected-test.md](reports/chunks-v2/chunk-local-selected-test.md)
- [reports/ci/container-persistence.json](reports/ci/container-persistence.json)
- [reports/ci/container-smoke.json](reports/ci/container-smoke.json)
- [reports/ci/provenance.json](reports/ci/provenance.json)
- [reports/ci/tests.json](reports/ci/tests.json)
- [reports/ci/tests.md](reports/ci/tests.md)
- [reports/ci-status.json](reports/ci-status.json)
- [reports/live-api-smoke.json](reports/live-api-smoke.json)
- [reports/live-api-smoke.md](reports/live-api-smoke.md)
- [reports/runtime-verification.json](reports/runtime-verification.json)
- [reports/store-benchmark.json](reports/store-benchmark.json)
- [reports/store-benchmark.md](reports/store-benchmark.md)
- [reports/tests.json](reports/tests.json)
- [reports/tests.md](reports/tests.md)
- [reports/vector-scale.json](reports/vector-scale.json)
- [reports/vector-scale.md](reports/vector-scale.md)

## 运行数据

`data/`、`pgdata/`、`.venv/`、`.git/`、缓存、日志和测试临时目录不是源码；源码包不包含这些目录，也不包含 `.env` 密钥。
