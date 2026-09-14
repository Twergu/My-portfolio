"""Update the README experiment table from measured reports, not constants."""
import json
from pathlib import Path

from backend.config import ROOT


def read(path):
    file=ROOT/path
    return json.loads(file.read_text(encoding='utf-8')) if file.exists() else {}


def number(value):
    return '待实测' if value is None else f'{value:.4f}'


def main():
    chunks=read('reports/chunks-v2/chunk-experiment-local.json')
    ci=read('reports/ci-status.json')
    scale=read('reports/vector-scale.json')
    local=read('reports/tests.json')
    pg=read('reports/ci/tests.json')
    stores=read('reports/store-benchmark.json')
    lines=['| 项目 | 实测结果与范围 |','|---|---|',
           f"| 本地测试 | {local.get('status','未执行')}，具体数量和时间见[动态报告](reports/tests.md) |",
           f"| CI / PostgreSQL 测试 | {ci.get('conclusion') or ci.get('status','待运行')}；[验收运行]({ci.get('html_url','https://github.com/Twergu/My-portfolio/actions')})，版本 `{ci.get('head_sha','')[:7]}`；[数据库测试报告](reports/ci/tests.md) |" if pg else
           '| CI / PostgreSQL 测试 | 等待 CI 报告；工作流要求全部执行，任何 skipped 均令验收失败 |']
    if chunks:
        retrieval=chunks['holdout']['retrieval']
        lines += [f"| 困难集 / 本地检索 | {chunks['dataset_id']}；test Recall@1/3/5 = " +
                  ' / '.join(number(retrieval.get(f'recall_at_{k}',{}).get('mean')) for k in (1,3,5)) +
                  f"；MRR={number(retrieval['mrr_at_k']['mean'])}，nDCG={number(retrieval['ndcg_at_k']['mean'])} |",
                  f"| Chunk 实验 | 六组配置；dev 选择 {chunks['selected']['size']}/{chunks['selected']['overlap']}，仅适用本地基线；[完整结果](reports/chunks-v2/chunk-experiment-local.md) |"]
    for row in scale.get('results',[]):
        for mode in ('exact','hnsw'):
            result=row.get(mode,{})
            timing=result.get('query_latency_ms',{})
            lines.append(f"| {row['count']:,} chunks / {mode} | {row['status']}：P50/P95 = {number(timing.get('p50'))}/{number(timing.get('p95'))} ms；Recall@5={number(result.get('recall_at_k_against_independent_exact'))} |")
    if scale:
        lines.append('| Vector Benchmark | [硬件、方法、构建耗时与索引大小](reports/vector-scale.md)；合成向量、单客户端、热缓存，不代表语义检索质量 |')
    if stores.get('comparison_complete'):
        values=stores['backends']
        lines.append('| SQLite vs pgvector / 1k | P50 ms：' + ' / '.join(
            name + ' ' + number(values[name]['query_latency_ms']['p50'])
            for name in ('sqlite_exact','pgvector_exact','pgvector_hnsw')) + '；[对照报告](reports/store-benchmark.md) |')
    container=read('reports/ci/container-persistence.json')
    lines += [f"| Docker | {container.get('status','待实测')}：App + pgvector、PDF 索引与引用、应用重启持久性；[验收数据](reports/ci/container-persistence.json) |" if container else
              '| Docker | 等待实际容器验收报告 |',
              '| 真实 API 质量 / 成本 | 按用户要求暂缓付费调用。Answer Correctness、Citation Groundedness、Refusal Accuracy、真实模型 P50/P95 和 cost/query 尚无有效实测值 |',
              '', '以上数据来自 JSON 运行快照，使用 `python -m scripts.results_summary` 更新。测试数量始终引用自动报告；本地哈希检索分数不等于真实模型准确率。']
    if scale.get('status')=='completed':
        lines.append('HNSW 表格使用 ef_search=100；完整报告另列 400/1000 的召回与延时。默认仍选 Exact，只有目标数据的召回和延时都达标才切换 HNSW。CI 的 Docker 验收来自全新 Linux runner，本机尚未安装 Docker。')
    path=ROOT/'README.md'; text=path.read_text(encoding='utf-8')
    start='<!-- EXPERIMENT_RESULTS_START -->'; end='<!-- EXPERIMENT_RESULTS_END -->'
    if start not in text or end not in text: raise ValueError('README markers missing')
    text=text.split(start)[0]+start+'\n'+'\n'.join(lines)+'\n'+end+text.split(end,1)[1]
    path.write_text(text,encoding='utf-8')


if __name__=='__main__':
    main()
