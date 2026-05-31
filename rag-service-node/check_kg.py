import json
import traceback
from app.services.kg_retrieval.service import KGRetrievalService

svc = KGRetrievalService()
tests = [
    ("artifact_museum_query", {"artifact_name": "Tea Bowl and Dish"}),
    ("museum_count_query", {"museum_name": "Art Institute of Chicago"}),
    ("recommended_artifacts_query", {"artifact_name": "Tea Bowl and Dish"}),
    ("artifact_description_query", {"artifact_name": "女史箴图"}),
]

for template, params in tests:
    try:
        res = svc.retrieve(template, "q", params)
        if res is None:
            print(json.dumps({"template": template, "result": None}, ensure_ascii=False))
            continue
        # Try to produce a compact summary
        out = {
            "template": template,
            "status": getattr(res, 'status', str(res)),
            "facts_count": len(getattr(res, 'facts', []) or []),
            "raw_records_count": len(getattr(res, 'raw_records', []) or []),
        }
        # include first raw record and first fact (if present) for quick inspection
        raw = getattr(res, 'raw_records', None)
        if raw:
            out['first_raw'] = raw[0]
        facts = getattr(res, 'facts', None)
        if facts:
            try:
                first = facts[0]
                out['first_fact'] = {
                    'subject': getattr(first, 'subject', None),
                    'predicate': getattr(first, 'predicate', None),
                    'object': getattr(first, 'object', None),
                    'source_name': getattr(first, 'source_name', None),
                    'source_url': getattr(first, 'source_url', None),
                }
            except Exception:
                out['first_fact'] = str(facts[0])
        print(json.dumps(out, ensure_ascii=False, default=str))
    except Exception as e:
        print(json.dumps({"template": template, "error": str(e), "trace": traceback.format_exc()}, ensure_ascii=False))
