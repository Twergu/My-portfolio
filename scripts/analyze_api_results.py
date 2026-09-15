"""Build the API results/expense summary from immutable measured reports."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from backend.config import ROOT
from backend.rag import chunks_from_pages
from scripts.evaluate import HARD_DATASET, load_dataset


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def mean(report, metric):
    return report['summary']['answer_quality'].get(metric, {}).get('mean')


def percent(value):
    return 'N/A' if value is None else f'{value:.2%}'


def main():
    dataset = load_dataset(HARD_DATASET)
    experiment = read('reports/chunks-api/chunk-experiment-api.json')
    holdout = read('reports/chunks-api/chunk-api-selected-test.json')
    assert experiment['status'] == 'completed' and holdout['quality_evaluation']['status'] == 'completed'
    layouts = defaultdict(list)
    for row in experiment['results']:
        layout = [[d['id'], c['page'], c['ordinal'], c['text']] for d in dataset['documents']
                  for c in chunks_from_pages(d['pages'], row['size'], row['overlap'])]
        digest = hashlib.sha256(json.dumps(layout, ensure_ascii=False).encode()).hexdigest()
        layouts[digest].append({'size': row['size'], 'overlap': row['overlap'], 'chunks': len(layout)})
    baseline = read('reports/chunks-api/chunk-api-450-0-dev.json')
    mini = read('reports/verifier-models/mini-450-0-dev.json')
    mode_reports = {mode: read(f'reports/verification/{mode}.json') for mode in ('off', 'fast', 'strict')}
    assert all(r['quality_evaluation']['status'] == 'completed' for r in mode_reports.values())
    # A strict report copied for mode comparison is the same paid run, not a new expense.
    paths = [p.relative_to(ROOT) for p in sorted((ROOT / 'reports/chunks-api').glob('chunk-api-*-dev.json'))]
    paths += [Path(p) for p in ('reports/chunks-api/chunk-api-selected-test.json',
        'reports/api-baseline-v1/chunk-api-900-120-dev.json', 'reports/verifier-models/mini-450-0-dev.json',
        'reports/verification/off.json', 'reports/verification/fast.json', 'reports/verification/strict.json')]
    ledger, seen = [], set()
    for path in paths:
        data = (ROOT / path).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        report = json.loads(data)
        ledger.append({'report': path.as_posix(), 'sha256': digest, 'queries': report['summary']['query_count'],
            'cost_usd': report['run_cost_usd'], 'application_cost_usd': report['summary']['cost_usd']['total'],
            'index_cost_usd': report['indexing']['metrics']['cost_usd'],
            'judge_cost_usd': report['quality_evaluation']['judge_cost_usd'],
            'status': report['quality_evaluation']['status']})
    for path in ('reports/live-api-smoke.json', 'reports/live-ui-smoke.json'):
        if not (ROOT / path).exists():
            continue
        report = read(path)
        ledger.append({'report': path, 'cost_usd': report.get('run_cost_usd', report.get('cost_usd')),
                       'status': report['status']})
    known = sum(r['cost_usd'] for r in ledger if r['cost_usd'] is not None)
    total = known if all(r['cost_usd'] is not None for r in ledger) else None
    failures = Counter()
    for row in holdout['queries']:
        if row.get('support', {}).get('failure_reason'):
            failures[row['support']['failure_reason']] += 1
    quality = holdout['summary']['answer_quality']
    result = {'dataset_id': dataset['dataset_id'], 'selected': experiment['selected'],
        'holdout_summary': holdout['summary'], 'chunk_layout_groups': list(layouts.values()),
        'holdout_failure_reasons': dict(failures), 'cost_ledger': ledger,
        'recorded_total_cost_usd': total, 'known_subtotal_cost_usd': known,
        'limitations': ['Synthetic multilingual policy corpus with related templates, not human-labeled production data.',
            'One run per configuration. Identical chunk layouts do not establish a chunk-size effect; API ranking/generation/Judge variation remains.',
            'Verifier pilot and mode comparison regenerate answers; not paired causal experiments.',
            'Judge judgments are automated. Citation scores apply to delivered answers only.',
            'Uniform configured prices and reported usage are estimates, not invoices. Failed original Judge cost is included in its repaired report; recovery snapshots and reused strict runs are not added twice.']}
    lines = ['# 真实 API 实验结果与费用', '',
        '模型：text-embedding-3-small → gpt-5.6-luna → gpt-5.6-luna；独立评估 Judge：gpt-4.1。', '',
        f"数据集：{dataset['dataset_id']}；六组 dev 配置后冻结 {experiment['selected']['size']}/{experiment['selected']['overlap']}，只对选中配置运行 test。", '',
        '| 测试集指标 | 得分 | 样本数 |', '|---|---:|---:|']
    for key in ('answer_correctness', 'citation_groundedness', 'refusal_accuracy', 'quote_match_failure',
                'unsupported_answer', 'false_refusal', 'grounding_rejected_correct_and_grounded'):
        score = quality.get(key, {'mean': None, 'count': 0})
        lines.append(f"| {key} | {percent(score['mean'])} | {score['count']} |")
    lines += ['', 'Citation Groundedness 只统计交付答案的逐题平均断言支持率；拒答没有答案可评分。False Refusal 包含生成拒答与校验拦截，不能全部解释成校验器错误。',
        '', '## 分块效应与选择范围', '',
        '| 产生相同文本边界的配置 | Chunk 数 |', '|---|---:|']
    for group in layouts.values():
        lines.append('| ' + ', '.join(f"{r['size']}/{r['overlap']}" for r in group) + f" | {group[0]['chunks']} |")
    lines += ['', '最佳 dev 得分用于冻结测试配置，不能据单次实验宣称普遍最优。相同边界配置间的得分差异不能归因于 Chunk Size/Overlap；本集仍需要真实长页资料补充。页级召回也不等于完整事实召回。',
        '', '## Verifier 模型独立配置试验', '',
        '同为 450/0 dev、strict、Luna 生成。每组各生成一次，答案不完全相同，保留随机性影响。', '',
        '| Verifier | Correctness | False refusal | P50 / P95 ms | Mean USD/query |', '|---|---:|---:|---:|---:|']
    for report in (baseline, mini):
        timing = report['summary']['latency_ms']['question_total']
        lines.append(f"| {report['configuration']['verifier_model']} | {percent(mean(report, 'answer_correctness'))} | {percent(mean(report, 'false_refusal'))} | {timing['p50']:.1f} / {timing['p95']:.1f} | {report['summary']['cost_usd']['average_per_query']:.8f} |")
    lines += ['', '该 pilot 证明可真实调用不同 Verifier，但不足以证明换模型必然改善；继续保留用户选择的 Luna/Luna 经济基线。',
        '', '验证模式详见 [off / fast / strict 对比](verification/comparison.md)。Runtime off/fast 不提供语义支持保证；本轮不根据 test 结果继续修改提示词或选模型。',
        '', '## 费用账本', '',
        '| 实际运行报告 | USD |', '|---|---:|']
    for row in ledger:
        path = row['report'].removeprefix('reports/')
        cost = '未知' if row['cost_usd'] is None else f"{row['cost_usd']:.8f}"
        lines.append(f'| [{path}]({path}) | {cost} |')
    lines += ['', f'有记录的已知估算费用合计：USD **{known:.8f}**；费用完整：{total is not None}。',
        '', '包含独立 Judge、索引、诊断基线和失败补评；应用 cost/query 另见逐题报告，不能将评估开销当作用户每次问答费用。复用的 strict 报告和修复前快照不重复收费计数。',
        '', '## 限制', ''] + ['- ' + value for value in result['limitations']]
    (ROOT / 'reports/api-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'reports/api-results.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
