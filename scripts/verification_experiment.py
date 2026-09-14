"""Explicit paid off/fast/strict comparison with an independent reference judge."""
import argparse
import json
import os
from pathlib import Path

from backend.config import environment_settings
from scripts.evaluate import HARD_DATASET, evaluate_dataset, load_dataset, provider_and_metrics, write_report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-api',action='store_true',required=True,help='Explicitly enable paid evaluation calls.')
    parser.add_argument('--dataset',type=Path,default=HARD_DATASET)
    parser.add_argument('--split',choices=('dev','test'),default='test')
    parser.add_argument('--judge-model',default=os.getenv('RAG_EVAL_JUDGE_MODEL',''))
    parser.add_argument('--output-dir',type=Path,default=Path('reports/verification'))
    args=parser.parse_args()
    key=os.getenv('RAG_API_KEY','')
    if not key or not args.judge_model:
        parser.error('API key and an explicit evaluation judge model are required.')
    settings=environment_settings().model_copy(update={'mode':'api','search_mode':'exact'})
    provider,_=provider_and_metrics('api'); reports=[]
    try:
        for mode in ('off','fast','strict'):
            candidate=settings.model_copy(update={'verification_mode':mode})
            report=evaluate_dataset(load_dataset(args.dataset),candidate,args.split,key,provider,judge_model=args.judge_model)
            write_report(report,args.output_dir/mode)
            reports.append({'mode':mode,'summary':report['summary'],'quality_evaluation':report['quality_evaluation']})
            if report['status']!='completed' or report['quality_evaluation']['status']!='completed':
                raise RuntimeError('Incomplete evaluation saved; comparison stopped.')
    finally:
        provider.close()
    (args.output_dir/'comparison.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
