# backend-spring

Spring Boot stub for China Library QA system. Provides a simple controller and mock service to support frontend development and integration testing.

## Run

Build:

```powershell
mvn -f backend-spring clean package -DskipTests
```

Run:

```powershell
java -jar backend-spring/target/backend-spring-0.1.0.jar
```

Default port: 8081

## Endpoints

- GET /api/qa/health
- POST /api/qa/ask
- POST /api/qa/feedback

## Notes

- This is a minimal stub. Replace QaServiceImpl.ask with real orchestration logic when rag-service-node interface is stable.
- application.yml contains `qa.rag.url` which is the rag-service-node endpoint to call for real answers.
