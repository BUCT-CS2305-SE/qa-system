# backend-spring — 问答系统后端网关

Spring Boot 3.1.4 后端服务，作为前端与 RAG 服务之间的聚合/治理层，提供统一入口、鉴权、限流、转发、历史记录与反馈落库。

---

## 启动

```powershell
# 构建（跳过测试）
mvn -f backend-spring clean package -DskipTests

# 运行
java -jar backend-spring/target/backend-spring-0.1.0.jar

# 开发模式（Maven）
mvn -f backend-spring spring-boot:run
```

默认端口：**8081**

---

## 接口

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|:---:|
| `/api/qa/ask` | POST | 核心问答，转发至 RAG 服务 | 需要 |
| `/api/qa/feedback` | POST | 反馈记录，落库 + 转发 RAG | 需要 |
| `/api/qa/history/list` | GET | 按会话分页查询历史消息 | 需要 |
| `/api/qa/health` | GET | 健康检查 | 免鉴权 |

---

## 功能模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 问答入口 | `QaController.java` | 代理转发至 RAG，含重试 + 降级 |
| 历史查询 | `HistoryController.java` | H2 持久化，按 session_id 分页 |
| API 鉴权 | `ApiKeyFilter.java` | `X-Api-Key` 校验，health 免鉴权 |
| IP 限流 | `RateLimitFilter.java` | 滑动窗口 60s/60 次，超限 429 |
| CORS | `CorsConfig.java` | 允许 localhost + 局域网 IP |
| RAG 客户端 | `HttpRagClient.java` | RestTemplate 调 RAG，指数退避重试，JWT 透传 |
| 历史持久化 | `HistoryEntity.java` | H2 存储问答记录（含 sources/facts JSON） |
| 定时清理 | `HistoryCleanupJob.java` | 每日 03:10 清理 30 天前数据 |
| 反馈存储 | `FeedbackEntity.java` | 反馈记录 JPA |
| 监控 | `QaServiceImpl.java` | Micrometer 计数器（QPS/延迟/错误率） |

---

## 鉴权机制

双重鉴权：
1. `X-Api-Key` header（固定值 `qa-demo-key`）→ `ApiKeyFilter`
2. `Authorization` header（JWT token，由前端 localStorage 读取）→ 透传为 `X-Kg-Token` 给 RAG 服务

---

## 测试

```powershell
mvn -f backend-spring test            # JUnit 单元测试
mvn -f backend-spring checkstyle:check  # 代码风格检查
mvn -f backend-spring jacoco:report     # 覆盖率报告（target/site/jacoco/）
```

---

## 技术栈

- Spring Boot 3.1.4 · Java 17
- Spring Web · Spring Data JPA
- H2 Database（内嵌）
- Micrometer（指标监控）
- Checkstyle + JaCoCo（代码质量）
