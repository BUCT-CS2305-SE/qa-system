# 文物知识问答子系统 — 测试报告

版本：v1.0 | 测试日期：__________ | 测试人员：__________

---

## 一、测试概述

### 1.1 测试目标

验证文物知识问答子系统满足以下验收标准：

- [ ] 覆盖 ≥10 类简单问答并可演示
- [ ] no_data 兜底生效，无数据时不编造
- [ ] sources 可点击并指向详情页
- [ ] `POST /api/qa/ask` 响应结构稳定，前端可直接渲染
- [ ] `POST /api/qa/feedback` 反馈可记录
- [ ] `GET /api/health` 健康检查可用
- [ ] 多轮对话上下文继承正确
- [ ] 复杂问答（对比/统计/路径）可用
- [ ] 鉴权拦截未授权请求
- [ ] 限流超过阈值时返回 429

### 1.2 测试范围

| 模块 | 内容 |
|------|------|
| RAG 服务 | 输入理解、意图分类、实体抽取、KG检索、答案生成、溯源 |
| Spring Boot 网关 | 鉴权、限流、转发、历史记录、定时清理 |
| Web 前端 | 对话界面、来源展示、反馈按钮、多轮会话 |
| Docker 部署 | 三服务编排、健康检查、网络通信 |

### 1.3 测试环境

| 项目 | 配置 |
|------|------|
| RAG 服务 | Python 3.13 + FastAPI，端口 8000 |
| 后端网关 | Java 17 + Spring Boot 3.1.4，端口 8081 |
| Web 前端 | React 19 + Vite 8，端口 5173 |
| 知识图谱 | 数据组 API `https://se-cs2305.yazs.top`（hybrid 模式） |
| 测试工具 | pytest 19 用例 + 手动测试 33 条题集 |

---

## 二、测试用例

### 2.1 简单问答（12 类）

**测试方法**：每类用 2~3 个问题验证，检查返回 status=ok、intent 正确、answer 与预期相符、sources 非空。

| 编号 | 测试意图 | 测试问题 | 预期结果 | 实际结果 | 通过 |
|------|----------|----------|----------|----------|------|
| F-001 | artifact_museum | 女史箴图在哪个博物馆？ | status=ok, intent=artifact_museum, answer含"大英博物馆" | | |
| F-002 | artifact_museum | Admonitions Scroll在哪里？ | status=ok, answer含博物馆名 | | |
| F-003 | artifact_period | 青铜奔马属于哪个朝代？ | status=ok, intent=artifact_period, answer含朝代 | | |
| F-004 | artifact_period | 马踏飞燕是什么时期的？ | status=ok, answer含时期名 | | |
| F-005 | artifact_material | 马踏飞燕是什么材质的？ | status=ok, intent=artifact_material | | |
| F-006 | artifact_material | 清明上河图的材质是什么？ | status=ok, answer含材质 | | |
| F-007 | artifact_type | Tea Bowl and Dish属于什么类型？ | status=ok, intent=artifact_type | | |
| F-008 | artifact_description | 请介绍一下清明上河图 | status=ok, intent=artifact_description, answer含介绍文字 | | |
| F-009 | artifact_description | 介绍一下青铜奔马 | status=ok | | |
| F-010 | artifact_dimensions | 女史箴图的尺寸是多少？ | status=ok, intent=artifact_dimensions, answer含尺寸 | | |
| F-011 | artifact_dimensions | 清明上河图的规格是多少？ | status=ok | | |
| F-012 | painting_author | 清明上河图的作者是谁？ | status=ok, intent=painting_author, answer含"张择端" | | |
| F-013 | painting_author | 马踏飞燕的作者是谁？ | status=ok | | |
| F-014 | artist_biography | 顾恺之的生平经历是怎样的？ | status=ok, intent=artist_biography | | |
| F-015 | artist_biography | 张择端的生平是怎样的？ | status=ok, answer含生平信息 | | |
| F-016 | same_artist_works | 张择端还有哪些作品？ | status=ok, intent=same_artist_works, answer含作品列表 | | |
| F-017 | same_artist_works | 顾恺之还有哪些作品？ | status=ok | | |
| F-018 | dynasty_representative | 唐代有哪些代表性文物？ | status=ok, intent=dynasty_representative_artifacts, answer含文物列表 | | |
| F-019 | dynasty_representative | 宋代有什么代表文物？ | status=ok | | |
| F-020 | museum_count | 大都会博物馆共收藏了多少件？ | status=ok, intent=museum_count, answer含数字 | | |
| F-021 | museum_count | 英国博物馆有多少件中国文物？ | status=ok | | |
| F-022 | recommended_artifacts | 推荐一些和女史箴图类似的文物 | status=ok, intent=recommended_artifacts, answer含推荐列表 | | |

**小计**：___ / 22 通过

### 2.2 复杂问答（4 类）

| 编号 | 测试意图 | 测试问题 | 预期结果 | 实际结果 | 通过 |
|------|----------|----------|----------|----------|------|
| F-023 | compare_artifacts | 比较女史箴图和清明上河图 | status=ok, intent=compare_artifacts, answer含两文物属性对比 | | |
| F-024 | compare_artifacts | 比较Admonitions Scroll和青铜奔马 | status=ok | | |
| F-025 | artifact_statistics | 唐代文物统计 | status=ok, intent=artifact_statistics, answer含统计数字 | | |
| F-026 | artifact_statistics | 宋代文物统计 | status=ok | | |
| F-027 | path_query | 女史箴图的流转路径 | status=ok, intent=path_query, answer含路径信息 | | |
| F-028 | multi_hop | Admonitions Scroll经过哪些地方？ | status=ok, intent=multi_hop | | |

**小计**：___ / 6 通过

### 2.3 no_data 兜底

**测试方法**：使用不在知识图谱中的文物名或编造的问题，验证返回 no_data 而非编造答案。

| 编号 | 测试问题 | 预期 no_data=true | 预期 answer="暂无相关数据" | 预期不包含编造内容 | 通过 |
|------|----------|-------------------|---------------------------|---------------------|------|
| ND-001 | 一块不知名石头的材质是什么？ | ☐ | ☐ | ☐ | |
| ND-002 | abcdefg在哪个博物馆？ | ☐ | ☐ | ☐ | |
| ND-003 | 不存在的文物123的介绍 | ☐ | ☐ | ☐ | |
| ND-004 | 火星文物的作者是谁？ | ☐ | ☐ | ☐ | |
| ND-005 | ZZZZZZ博物馆收藏了多少件？ | ☐ | ☐ | ☐ | |

**小计**：___ / 5 通过

### 2.4 多轮对话

**测试方法**：连续发送多条消息，验证代词指代和话题切换。

**场景一：代词指代**

| 步骤 | 输入 | 预期 | 实际 | 通过 |
|------|------|------|------|------|
| 1 | 女史箴图在哪个博物馆？ | 正常回答，含博物馆 | | |
| 2 | 它的材质是什么？ | "它"指代女史箴图，回答材质信息 | | |
| 3 | 它的尺寸呢？ | 继续指代女史箴图，回答尺寸 | | |

**场景二：话题切换**

| 步骤 | 输入 | 预期 | 实际 | 通过 |
|------|------|------|------|------|
| 1 | 女史箴图在哪里？ | 正常回答 | | |
| 2 | 换个话题，清明上河图的作者是谁？ | 检测到话题切换，回答张择端 | | |
| 3 | 它的收藏地呢？ | "它"指代清明上河图，而非女史箴图 | | |

**场景三：无上下文时问代词**

| 步骤 | 输入 | 预期 | 实际 | 通过 |
|------|------|------|------|------|
| 1 | 它的材质是什么？ | 无法确定指代对象，返回 clarify 或 no_data | | |

**小计**：___ / 7 步 通过

### 2.5 来源溯源

**测试方法**：每条正常回答（status=ok）是否包含 sources，sources 中是否有 source_name 和 detail_url。

| 编号 | 验证项 | 预期 | 实际 | 通过 |
|------|--------|------|------|------|
| S-001 | 女史箴图的回答是否含 sources | sources 非空，含 source_name 和 detail_url | | |
| S-002 | sources 中 detail_url 是否可点击 | 前端渲染为可点击链接 | | |
| S-003 | no_data 的回答 sources 是否为空 | sources=[] 或明确标注"无来源" | | |
| S-004 | 对比回答的 sources 是否含来源 | 至少一个 source 信息 | | |

**小计**：___ / 4 通过

### 2.6 反馈机制

| 编号 | 操作 | 预期 | 实际 | 通过 |
|------|------|------|------|------|
| FB-001 | 在任意助手回答上点 👍 | 按钮高亮为"有帮助"状态，不掉报错 | | |
| FB-002 | 在任意助手回答上点 👎 | 按钮高亮为"不准确"状态 | | |
| FB-003 | 切换会话后再切回 | 之前的反馈状态保留 | | |
| FB-004 | 对同一条回答先点 👍 再点 👎 | 切换为最新的反馈状态 | | |

**小计**：___ / 4 通过

### 2.7 鉴权与限流

| 编号 | 测试项 | 请求 | 预期 HTTP 状态码 | 实际 | 通过 |
|------|--------|------|------------------|------|------|
| A-001 | 无 API Key | `curl localhost:8081/api/qa/ask -H "Content-Type: application/json" -d '{"question":"test"}'` | 401 | | |
| A-002 | 错误 API Key | 同上，Header 设为 `X-Api-Key: wrong-key` | 401 | | |
| A-003 | 正确 API Key | Header 设为 `X-Api-Key: qa-demo-key` | 200 | | |
| A-004 | health 免鉴权 | `curl localhost:8081/api/qa/health` | 200（无需ApiKey） | | |
| A-005 | 快速连续发 61 次请求 | 1分钟内发超过60次 | 第61次返回 429 | | |

**小计**：___ / 5 通过

### 2.8 健康检查

| 编号 | 服务 | 请求 | 预期 | 实际 | 通过 |
|------|------|------|------|------|------|
| H-001 | RAG 服务 | `curl localhost:8000/api/health` | `{"status":"ok"}` | | |
| H-002 | 后端网关 | `curl localhost:8081/api/qa/health` | `{"status":"ok"}` | | |

**小计**：___ / 2 通过

### 2.9 Docker 部署验证

| 编号 | 验证项 | 预期 | 实际 | 通过 |
|------|--------|------|------|------|
| D-001 | `docker-compose up -d` 启动 | 三个容器全部 Running，无错误日志 | | |
| D-002 | RAG 服务端口可达 | `curl localhost:8000/api/health` 返回 ok | | |
| D-003 | 后端端口可达 | `curl localhost:8081/api/qa/health` 返回 ok | | |
| D-004 | 前端可访问 | 浏览器 `localhost:5173` 显示页面 | | |
| D-005 | `docker-compose down` 停止 | 容器全部停止，无残留 | | |

**小计**：___ / 5 通过

---

## 三、缺陷记录

| 编号 | 严重程度 | 模块 | 问题描述 | 复现步骤 | 状态 | 解决方式 |
|------|----------|------|----------|----------|------|----------|
| B-001 | | | | | | |
| B-002 | | | | | | |
| B-003 | | | | | | |

> 严重程度：致命 / 严重 / 一般 / 提示

---

## 四、测试结果汇总

### 4.1 通过率

| 测试类别 | 用例数 | 通过 | 失败 | 通过率 |
|----------|--------|------|------|--------|
| 简单问答 | 22 | | | |
| 复杂问答 | 6 | | | |
| no_data 兜底 | 5 | | | |
| 多轮对话 | 7 | | | |
| 来源溯源 | 4 | | | |
| 反馈机制 | 4 | | | |
| 鉴权与限流 | 5 | | | |
| 健康检查 | 2 | | | |
| Docker 部署 | 5 | | | |
| **合计** | **60** | | | |

### 4.2 自动化测试

RAG 服务单元测试（pytest）：

```
运行命令：cd rag-service-node && python -m pytest tests/test_pipeline.py -v
测试用例数：19
通过数：__________
失败数：__________
```

### 4.3 性能指标

| 指标 | 目标 | 实测值 |
|------|------|--------|
| 简单问答平均响应时间 | < 2s（不含冷启动） | |
| LLM 生成场景 | 无硬性要求，需可配置超时 | |
| 100并发下的可用性 | 无硬性要求 | |

---

## 五、测试结论

- [ ] 所有 P0 功能通过验收
- [ ] no_data 兜底机制生效
- [ ] 来源溯源完整可用
- [ ] 鉴权与限流生效
- [ ] Docker 部署正常
- [ ] 无致命/严重缺陷遗留

**测试结论**：__________

**签字**：__________ &emsp; **日期**：__________
