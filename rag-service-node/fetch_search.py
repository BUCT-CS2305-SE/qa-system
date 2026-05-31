import json
from app.services.kg_retrieval.service import KGRetrievalService

svc = KGRetrievalService()
queries = [
    "女史箴图",
    "女史箴图卷",
    "Nushi Zhen Tu",
    "Portrait of the Lady",
    "Nushizhen",
]

for q in queries:
    try:
        print('--- Query:', q)
        payload = svc._get_json(f"/api/search?q={q}&page=1&page_size=10")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception as e:
        print('ERROR', e)
