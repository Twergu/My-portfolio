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
    api=read('reports/chunks-api/chunk-api-selected-test.json')
    smoke=read('reports/live-api-smoke.json')
    api_chunks=read('reports/chunks-api/chunk-experiment-api.json')
    modes=read('reports/verification/comparison.json')
    expenses=read('reports/api-results.json')
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
              f"| 真实 API 流程 | {smoke.get('status','待验证')}；PDF→Embedding→结构化回答→原文/断言校验→物理页引用；[真实 smoke](reports/live-api-smoke.md) |",
              '', '以上数据来自 JSON 运行快照，使用 `python -m scripts.results_summary` 更新。测试数量始终引用自动报告；本地哈希检索分数不等于真实模型准确率。']
    if api.get('status')=='completed' and api.get('quality_evaluation',{}).get('status')=='completed':
        summary=api['summary']; quality=summary['answer_quality']; retrieval=summary['retrieval']
        def mean(name): return number(quality.get(name,{}).get('mean'))
        timing=summary['latency_ms']['question_total']
        lines += ['', '| 真实 RAG 测试集 | 实测结果 |','|---|---|',
            f"| 版本 / 范围 | {api['dataset_id']}；{summary['query_count']} 题；{api['configuration']['chat_model']} / verifier {api['configuration']['verifier_model']}；[完整逐题结果](reports/chunks-api/chunk-api-selected-test.md) |",
            '| Recall@1/3/5 | '+' / '.join(number(retrieval[f'recall_at_{k}']['mean']) for k in (1,3,5))+' |',
            f"| MRR / nDCG | {number(retrieval['mrr_at_k']['mean'])} / {number(retrieval['ndcg_at_k']['mean'])} |",
            f"| Correctness / Citation Groundedness / Refusal Accuracy | {mean('answer_correctness')} / {mean('citation_groundedness')} / {mean('refusal_accuracy')} |",
            f"| Quote mismatch / Unsupported / False refusal | {mean('quote_match_failure')} / {mean('unsupported_answer')} / {mean('false_refusal')} |",
            f"| Query P50 / P95 | {number(timing['p50'])} / {number(timing['p95'])} ms；{api.get('concurrency',1)} workers；不含额外 Judge |",
            f"| 平均应用 cost/query | USD {summary['cost_usd']['average_per_query']:.8f} |" if summary['cost_usd']['average_per_query'] is not None else '| 平均应用 cost/query | 用量不完整，未知 |',
            f"| 实验与额外评估开销 | [分块对比](reports/chunks-api/chunk-experiment-api.md)；[验证模式](reports/verification/comparison.md)；Judge 不计入用户 query 成本 |",
            '', '答案正确性与引用支持度分别调用独立 Judge，引用评分看不到 gold evidence。指标分母及限制见评估协议；单次合成集结果仍需真实资料与人工复核。']
        if api_chunks.get('status')=='completed':
            selected=api_chunks['selected']
            lines.append(f"真实 API 开发集冻结 **{selected['size']}/{selected['overlap']}**。900/1200 的四组配置产生相同文本边界，单次得分差异不足以证明分块效应；[边界分析与费用账本](reports/api-results.md)。本机演示已使用冻结配置，代码的通用默认值仍需目标文档验证。")
        if modes:
            lines += ['', '| 验证模式（同一 test） | Correctness | False refusal | P50 / P95 ms | 平均 USD/query |',
                      '|---|---:|---:|---:|---:|']
            for row in modes:
                s=row['summary']; q=s['answer_quality']; t=s['latency_ms']['question_total']
                cost=s['cost_usd']['average_per_query']
                lines.append(f"| {row['mode']} | {number(q['answer_correctness']['mean'])} | {number(q['false_refusal']['mean'])} | {number(t['p50'])} / {number(t['p95'])} | {cost:.8f} |" if cost is not None else f"| {row['mode']} | 用量不完整，详见报告 | — | — | 未知 |")
            lines.append('各模式独立生成一次，存在随机性，不能当作相同答案的因果对照。off/fast 在运行时没有语义依据保证；当前 strict 有误拦截，保留风险说明而不根据 test 成绩继续改提示词。')
        if expenses.get('recorded_total_cost_usd') is not None:
            lines.append(f"本轮有记录的实际调用估算总费用 **USD {expenses['recorded_total_cost_usd']:.6f}**，含索引、额外 Judge、诊断基线和补评；不含税费，不能替代账单。")
    else:
        lines.append('真实 API smoke 已恢复执行；完整质量、分块和验证模式结果以各报告的完成状态为准。')
    if scale.get('status')=='completed':
        lines.append('HNSW 表格使用 ef_search=100；完整报告另列 400/1000 的召回与延时。默认仍选 Exact，只有目标数据的召回和延时都达标才切换 HNSW。CI 的 Docker 验收来自全新 Linux runner，本机尚未安装 Docker。')
    path=ROOT/'README.md'; text=path.read_text(encoding='utf-8')
    start='<!-- EXPERIMENT_RESULTS_START -->'; end='<!-- EXPERIMENT_RESULTS_END -->'
    if start not in text or end not in text: raise ValueError('README markers missing')
    text=text.split(start)[0]+start+'\n'+'\n'.join(lines)+'\n'+end+text.split(end,1)[1]
    path.write_text(text,encoding='utf-8')


if __name__=='__main__':
    main()
