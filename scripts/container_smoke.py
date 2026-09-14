"""Exercise a running Compose app over real HTTP, including PDF persistence."""
import argparse
import json
import time
from pathlib import Path

import httpx


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8000')
    parser.add_argument('--check-persistence',action='store_true')
    args=parser.parse_args()
    with httpx.Client(base_url=args.url,timeout=15) as client:
        health=client.get('/api/health'); health.raise_for_status()
        assert health.json()['storage']=='pgvector'
        if not args.check_persistence:
            response=client.post('/api/documents/sample'); response.raise_for_status()
        for _ in range(60):
            documents=client.get('/api/documents').json()['documents']
            if documents and all(doc['status']=='ready' for doc in documents):
                break
            if any(doc['status']=='error' for doc in documents):
                raise RuntimeError('Container PDF indexing failed')
            time.sleep(1)
        else:
            raise RuntimeError('Container PDF indexing timed out')
        response=client.post('/api/chat',json={'question':'员工年假如何申请？','language':'zh'})
        response.raise_for_status(); result=response.json()
        assert result['status']=='retrieval_only' and result['sources']
        for source in result['sources']:
            assert client.get(source['url'].split('#')[0]).content.startswith(b'%PDF-')
    Path('reports').mkdir(exist_ok=True)
    output=Path('reports/container-persistence.json' if args.check_persistence else 'reports/container-smoke.json')
    output.write_text(json.dumps({'status':'passed','storage':'pgvector','pdf_citations':True,
        'restart_persistence':args.check_persistence},indent=2)+'\n',encoding='utf-8')
    print('Container smoke passed')


if __name__=='__main__':
    main()
