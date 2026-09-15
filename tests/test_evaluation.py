import copy
import math

import pytest

from backend.config import Settings
from evals.metrics import aggregate, answer_metrics, percentile, retrieval_metrics, token_f1
from scripts.chunk_experiment import choose_configuration
from scripts.evaluate import evaluate_dataset, load_dataset


def source(page, document_id='manual'):
    return {'document_id': document_id, 'page': page}


def test_duplicate_chunks_cannot_inflate_page_retrieval_scores():
    result = retrieval_metrics([source(1), source(1), source(3), source(2)],
                               [source(1) | {'grade': 2}, source(2) | {'grade': 1}], 3)
    assert result['recall_at_k'] == 1
    assert result['precision_at_k'] == pytest.approx(2 / 3)
    assert result['mrr_at_k'] == 1
    assert result['ndcg_at_k'] == pytest.approx((3 + 1 / math.log2(4)) / (3 + 1 / math.log2(3)))


def test_missing_slots_and_unanswerable_queries_have_explicit_semantics():
    assert retrieval_metrics([source(1)], [source(1) | {'grade': 2}], 5)['precision_at_k'] == .2
    result = retrieval_metrics([source(1)], [], 5)
    assert result['recall_at_k'] is None
    assert result['any_retrieval_for_unanswerable'] is True
    assert retrieval_metrics([], [source(1) | {'grade': 2}], 5)['ndcg_at_k'] == 0


def test_local_excerpt_is_never_scored_as_a_generated_answer():
    query = {'answerable': True, 'expected_facts': [{'aliases': ['18 days']}], 'reference_answer': '18 days'}
    result = answer_metrics({'mode': 'local', 'answer': '18 days', 'status': 'retrieval_only'}, query)
    assert result['expected_facts_coverage_lexical'] is None
    assert result['claim_groundedness'] is None


def test_verification_failure_is_not_credited_as_correct_refusal():
    query = {'answerable': False, 'expected_facts': [], 'reference_answer': ''}
    assert answer_metrics({'mode': 'api', 'status': 'unsupported_answer'}, query)['correct_refusal'] == 0
    assert answer_metrics({'mode': 'api', 'status': 'insufficient_evidence'}, query)['correct_refusal'] == 1


def test_groundedness_includes_rejected_candidate_claims():
    query = {'answerable': True, 'expected_facts': [{'aliases': ['18 days']}], 'reference_answer': '18 days'}
    result = answer_metrics({'mode': 'api', 'answer': '', 'status': 'unsupported_answer', 'claims': [],
                             'support': {'total_claims': 2, 'verified_claims': 1}}, query)
    assert result['claim_groundedness'] == .5
    assert result['all_claims_grounded'] is False
    assert result['expected_facts_coverage_lexical'] == 0


def test_multilingual_lexical_scores_and_percentile_are_deterministic():
    assert token_f1('休暇は１８日です。[1]', '休暇は18日です。') == 1
    assert token_f1('18 days', '18 days annually') == pytest.approx(.8)
    assert percentile([10, 20, 30, 40], 95) == pytest.approx(38.5)
    assert percentile([], 95) is None


def test_unknown_cost_is_not_silently_reported_as_zero():
    row = {'status': 'answered', 'retrieval': {'recall_at_k': 1}, 'answer_quality': {}, 'elapsed_ms': 1,
           'metrics': {'cost_usd': None}}
    summary = aggregate([row, row | {'metrics': {'cost_usd': .02}}])
    assert summary['cost_usd']['total'] is None
    assert summary['cost_usd']['known_subtotal'] == .02
    assert summary['cost_usd']['unknown_questions'] == 1


def test_dataset_ground_truth_and_holdout_are_valid():
    dataset = load_dataset()
    assert {query['language'] for query in dataset['queries']} == {'zh', 'ja', 'en'}
    assert {query['category'] for query in dataset['queries']} == {'direct', 'cross_page', 'negative', 'adversarial'}
    dev = {query['id'] for query in dataset['queries'] if query['split'] == 'dev'}
    test = {query['id'] for query in dataset['queries'] if query['split'] == 'test'}
    assert dev and test and not dev.intersection(test)
    assert all(len(query['relevance']) >= 2 for query in dataset['queries'] if query['category'] == 'cross_page')


def test_parameter_selection_rejects_test_data():
    with pytest.raises(ValueError, match='dev'):
        choose_configuration([{'split': 'test'}])


def test_real_local_evaluation_uses_isolated_index_and_reports_no_api_cost():
    dataset = copy.deepcopy(load_dataset())
    dataset['documents'] = [document for document in dataset['documents'] if document['language'] == 'ja']
    dataset['queries'] = [query for query in dataset['queries'] if query['id'] == 'ja-04']
    report = evaluate_dataset(dataset, Settings(mode='local'), split='dev')
    assert report['summary']['query_count'] == 1
    assert report['summary']['retrieval']['recall_at_k']['mean'] == 1
    assert report['run_cost_usd'] == 0
    assert report['queries'][0]['metrics']['attempt_count'] == 0
    assert report['summary']['answer_quality']['expected_facts_coverage_lexical']['count'] == 0


def test_identical_chunk_boundaries_have_reproducible_tied_rankings(tmp_path):
    from backend.store import Store
    from backend.rag import local_vector
    from scripts.evaluate import build_index
    dataset = {'documents': [{'id':'ties','name':'ties.pdf','pages':[
        {'page':n,'text':'identical policy words' + '!'*n} for n in range(1,8)]}]}
    snapshots = []
    for size in (900,1200):
        store = Store(tmp_path / str(size))
        settings = Settings(mode='local', chunk_size=size)
        build_index(store,dataset,settings,'',None)
        snapshots.append((store.get_chunks('ties'),store.search(local_vector('policy'),settings.profile,top_k=3)))
        store.close()
    assert snapshots[0] == snapshots[1]


def test_parallel_evaluation_and_resume_preserve_inputs_and_query_metrics(tmp_path):
    from scripts.evaluate import write_report
    from scripts.chunk_experiment import reusable_report
    dataset = copy.deepcopy(load_dataset())
    dataset['documents'] = [d for d in dataset['documents'] if d['language']=='ja']
    dataset['queries'] = [q for q in dataset['queries'] if q['language']=='ja' and q['split']=='dev'][:3]
    settings = Settings(mode='local')
    progress = []
    parallel = evaluate_dataset(dataset,settings,'dev',concurrency=2,
        progress=lambda done,total,row: progress.append((done,total,row['id'])))
    sequential = evaluate_dataset(dataset,settings,'dev')
    assert parallel['summary']['retrieval'] == sequential['summary']['retrieval']
    assert parallel['run_cost_usd'] == 0
    assert [item[2] for item in progress] == [q['id'] for q in dataset['queries']]
    output = tmp_path/'cached'
    write_report(parallel,output)
    assert reusable_report(output.with_suffix('.json'),dataset,settings,'dev','',2) == parallel
    with pytest.raises(ValueError,match='different inputs'):
        reusable_report(output.with_suffix('.json'),dataset,settings,'dev','',1)
    altered=copy.deepcopy(dataset)
    altered['documents'][0]['pages'][0]['text']+=' changed policy'
    with pytest.raises(ValueError,match='different inputs'):
        reusable_report(output.with_suffix('.json'),altered,settings,'dev','',2)
