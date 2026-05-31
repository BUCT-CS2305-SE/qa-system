from app.orchestration.qa_pipeline import QAPipeline
from app.models.api import QAAskRequest

pipeline = QAPipeline()
req = QAAskRequest(question="女史箴图现藏于哪家博物馆？", mode="rule")
print("--- calling understanding ---")
understanding = pipeline.understanding_service.understand(req.question, req.session_id)
print(understanding.model_dump())
print("--- building query plan ---")
query_plan = pipeline.query_builder.build(understanding)
print(query_plan.model_dump())
print("--- retrieving ---")
retrieval = pipeline.retrieval_service.retrieve(query_plan.template_name, query_plan.query_text, query_plan.parameters)
print(retrieval.model_dump())
print("last_queries:", getattr(pipeline.retrieval_service, '_last_queries', None))
print("--- generating answer ---")
if retrieval and retrieval.status == 'ok':
    generated = pipeline.answer_service.generate(understanding, retrieval)
    print(generated.model_dump())
print("--- pipeline handle_question ---")
resp = pipeline.handle_question(req)
print(resp.model_dump())
