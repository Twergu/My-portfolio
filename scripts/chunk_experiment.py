"""Compare six page-preserving chunk policies using dev queries only."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import environment_settings
from scripts.evaluate import HARD_DATASET, evaluate_dataset, load_dataset, provider_and_metrics, write_report, display

GRID = [(450, 0), (450, 60), (900, 0), (900, 120), (1200, 120), (1200, 180)]


def choose_configuration(reports):
    if not reports or any(report['split'] != 'dev' or report.get('status', 'completed') != 'completed' for report in reports):
        raise ValueError('Only non-empty dev results can be used to select chunk parameters')
    # Fixed ahead of the run. Latency is not a tie breaker because a single pass
    # is noisy; using chunk count avoids selecting timer noise on this tiny set.
    def quality(report):
        score = report['summary'].get('answer_quality',{}).get('answer_correctness',{})
        return score.get('mean') if score.get('count') and score.get('mean') is not None else -1
    return max(reports, key=lambda report: (quality(report), report['summary']['retrieval']['recall_at_k']['mean'],
                                            report['summary']['retrieval']['ndcg_at_k']['mean'],
                                            -report['indexing']['chunk_count']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('local', 'api'), default='local')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'evals' / 'reports')
    parser.add_argument('--dataset', type=Path, default=HARD_DATASET)
    parser.add_argument('--judge-model', default=os.getenv('RAG_EVAL_JUDGE_MODEL',''))
    args = parser.parse_args()
    key = os.getenv('RAG_API_KEY', '')
    if args.mode == 'api' and not key:
        parser.error('RAG_API_KEY is missing; no API request was made.')
    if args.mode == 'api' and not args.judge_model:
        parser.error('An evaluation judge model is required; no API request was made.')
    settings = environment_settings().model_copy(update={'mode': args.mode, 'search_mode': 'exact'})
    dataset = load_dataset(args.dataset)
    provider, _ = provider_and_metrics(args.mode)
    reports = []
    try:
        for size, overlap in GRID:
            candidate = settings.model_copy(update={'chunk_size': size, 'chunk_overlap': overlap})
            report = evaluate_dataset(dataset, candidate, split='dev', api_key=key, provider=provider, judge_model=args.judge_model)
            reports.append(report)
            write_report(report, args.output_dir / f'chunk-{args.mode}-{size}-{overlap}-dev')
            if report['status'] != 'completed' or (args.mode == 'api' and report['quality_evaluation']['status'] != 'completed'):
                raise RuntimeError('Chunk experiment stopped: provider errors were saved in the configuration report; incomplete metrics cannot select parameters.')
            print(f'Completed dev: size={size}, overlap={overlap}, chunks={report["indexing"]["chunk_count"]}')
        winner = choose_configuration(reports)
        selected = winner['configuration']
        # Run the held-out questions only after selecting and freezing parameters.
        final_settings = settings.model_copy(update={'chunk_size': selected['chunk_size'], 'chunk_overlap': selected['chunk_overlap']})
        holdout = evaluate_dataset(dataset, final_settings, split='test', api_key=key, provider=provider, judge_model=args.judge_model)
        write_report(holdout, args.output_dir / f'chunk-{args.mode}-selected-test')
        if holdout['status'] != 'completed' or (args.mode == 'api' and holdout['quality_evaluation']['status'] != 'completed'):
            raise RuntimeError('Holdout evaluation failed; partial report saved, no completed experiment published.')
    finally:
        if provider is not None:
            provider.close()
    rows = [{'size': report['configuration']['chunk_size'], 'overlap': report['configuration']['chunk_overlap'],
             'chunk_count': report['indexing']['chunk_count'], 'indexing_ms': report['indexing']['elapsed_ms'],
             'recall_at_k': report['summary']['retrieval']['recall_at_k']['mean'],
             'precision_at_k': report['summary']['retrieval']['precision_at_k']['mean'],
             'mrr_at_k': report['summary']['retrieval']['mrr_at_k']['mean'],
             'ndcg_at_k': report['summary']['retrieval']['ndcg_at_k']['mean'],
             'answer_correctness':report['summary']['answer_quality'].get('answer_correctness',{}).get('mean'),
             'recall_at_1':report['summary']['retrieval'].get('recall_at_1',{}).get('mean'),
             'recall_at_3':report['summary']['retrieval'].get('recall_at_3',{}).get('mean'),
             'false_refusal':report['summary']['answer_quality'].get('false_refusal',{}).get('mean'),
             'question_p50_ms': report['summary']['latency_ms']['question_total']['p50'],
             'question_p95_ms': report['summary']['latency_ms']['question_total']['p95'],
             'run_cost_usd': report['run_cost_usd']} for report in reports]
    combined = {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(),
                'mode': args.mode, 'dataset_id': dataset['dataset_id'], 'tuning_split': 'dev',
                'selection_rule': 'Max dev Answer Correctness when judged, then Recall@k, nDCG@k, then fewest chunks; never test metrics.',
                'status':'completed' if holdout['status']=='completed' else 'failed',
                'chunk_unit': 'Unicode characters, adjusted toward sentence boundaries; physical pages never merged.',
                'results': rows, 'selected': {'size': selected['chunk_size'], 'overlap': selected['chunk_overlap']},
                'holdout': holdout['summary'], 'limitations': dataset['limitations'] + [
                    'One pass on a tiny corpus; p95 is descriptive, not a statistically stable production estimate.',
                    'Local hashed retrieval is a baseline, not a multilingual embedding model.',
                    'Changing production defaults is a separate decision; this script only reports results.']}
    output = args.output_dir / f'chunk-experiment-{args.mode}'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix('.json').write_text(json.dumps(combined, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [f'# Chunk experiment ({args.mode})', '', combined['selection_rule'], '', combined['chunk_unit'], '',
             '| Size | Overlap | Chunks | Recall@k | Precision@k | MRR@k | nDCG@k | Correctness | Recall@1 | Recall@3 | False refusal | Index ms | Query p50 ms | Query p95 ms | USD |',
             '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for row in rows:
        lines.append('| ' + ' | '.join(display(row[key]) for key in ('size', 'overlap', 'chunk_count', 'recall_at_k',
                     'precision_at_k', 'mrr_at_k', 'ndcg_at_k', 'answer_correctness', 'recall_at_1', 'recall_at_3', 'false_refusal',
                     'indexing_ms', 'question_p50_ms', 'question_p95_ms', 'run_cost_usd')) + ' |')
    lines += ['', f"Selected on dev: size **{selected['chunk_size']}**, overlap **{selected['chunk_overlap']}**.",
              f"Frozen test Recall@k: {display(holdout['summary']['retrieval']['recall_at_k']['mean'])}; test nDCG@k: {display(holdout['summary']['retrieval']['ndcg_at_k']['mean'])}.",
              '', 'The test split did not participate in parameter selection. Existing production defaults were not changed.', '',
              '## Limits', ''] + ['- ' + value for value in combined['limitations']]
    output.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report: {output.with_suffix(".md")}')


if __name__ == '__main__':
    main()
