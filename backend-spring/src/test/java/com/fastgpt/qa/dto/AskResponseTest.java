package com.fastgpt.qa.dto;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class AskResponseTest {

    private final ObjectMapper mapper = new ObjectMapper();

    @Test
    void shouldSerializeNoDataCorrectly() throws Exception {
        AskResponse resp = new AskResponse();
        resp.setRequestId("req-001");
        resp.setNoData(true);
        resp.setAnswer("暂无相关数据");
        resp.setStatus("no_data");
        resp.setCode(2001);

        String json = mapper.writeValueAsString(resp);
        assertTrue(json.contains("\"no_data\":true"));
        assertTrue(json.contains("\"暂无相关数据\""));
    }

    @Test
    void shouldSerializeSourcesCorrectly() throws Exception {
        AskResponse resp = new AskResponse();
        resp.setRequestId("req-002");
        resp.setSources(List.of(
                new AskResponse.Source("克利夫兰艺术博物馆", "https://example.com/detail/1"),
                new AskResponse.Source("大都会博物馆", "https://example.com/detail/2")
        ));

        String json = mapper.writeValueAsString(resp);
        assertTrue(json.contains("\"source_name\":\"克利夫兰艺术博物馆\""));
        assertTrue(json.contains("\"detail_url\":\"https://example.com/detail/1\""));
    }

    @Test
    void shouldDeserializeAskResponse() throws Exception {
        String json = """
                {
                    "request_id": "req-003",
                    "no_data": false,
                    "answer": "《女史箴图》现藏于大英博物馆。",
                    "sources": [
                        {"source_name": "大英博物馆", "detail_url": "https://www.britishmuseum.org/example"}
                    ],
                    "facts": [
                        {"subject": "女史箴图", "predicate": "museum", "object": "大英博物馆",
                         "source_name": "大英博物馆", "source_url": "https://www.britishmuseum.org/example"}
                    ],
                    "status": "ok",
                    "code": 0,
                    "intent": "artifact_museum",
                    "confidence": 0.95
                }""";

        AskResponse resp = mapper.readValue(json, AskResponse.class);
        assertEquals("req-003", resp.getRequestId());
        assertFalse(resp.getNoData());
        assertEquals("artifact_museum", resp.getIntent());
        assertEquals(1, resp.getSources().size());
        assertEquals("大英博物馆", resp.getSources().get(0).getSourceName());
    }

    @Test
    void isNoDataShouldReturnTrueWhenStatusIsNoData() {
        AskResponse resp = new AskResponse();
        resp.setStatus("no_data");
        assertTrue(resp.isNoData());
    }

    @Test
    void isNoDataShouldReturnTrueWhenNoDataFlagIsSet() {
        AskResponse resp = new AskResponse();
        resp.setNoData(true);
        assertTrue(resp.isNoData());
    }

    @Test
    void isNoDataShouldReturnTrueWhenStatusIsNull() {
        AskResponse resp = new AskResponse();
        assertTrue(resp.isNoData());
    }

    @Test
    void getSourceShouldReturnSourcesWhenPresent() {
        AskResponse resp = new AskResponse();
        List<AskResponse.Source> list = List.of(new AskResponse.Source("Museum", "url"));
        resp.setSources(list);
        assertEquals(1, resp.getSource().size());
    }

    @Test
    void getSourceShouldFallbackToSourceItem() {
        AskResponse resp = new AskResponse();
        resp.setSourceItem(new AskResponse.Source("Museum", "url"));
        assertEquals(1, resp.getSource().size());
        assertEquals("Museum", resp.getSource().get(0).getSourceName());
    }

    @Test
    void serializeDeserializeRoundtrip() throws Exception {
        AskResponse original = new AskResponse();
        original.setRequestId("req-100");
        original.setNoData(false);
        original.setAnswer("测试回答");
        original.setStatus("ok");
        original.setCode(0);
        original.setIntent("artifact_type");
        original.setConfidence(0.9);
        original.setLlmNote("LLM补充说明");
        original.setTraceId("trace-xyz");
        original.setSources(List.of(new AskResponse.Source("源A", "http://a.com")));

        String json = mapper.writeValueAsString(original);
        AskResponse restored = mapper.readValue(json, AskResponse.class);

        assertEquals(original.getRequestId(), restored.getRequestId());
        assertEquals(original.getAnswer(), restored.getAnswer());
        assertEquals(original.getIntent(), restored.getIntent());
        assertEquals(original.getSources().size(), restored.getSources().size());
        assertEquals("源A", restored.getSources().get(0).getSourceName());
    }

    @Test
    void answerShouldContainNoDataPhraseWhenNoData() {
        AskResponse resp = new AskResponse();
        resp.setNoData(true);
        resp.setAnswer("暂无相关数据");
        assertTrue(resp.getAnswer().contains("暂无相关数据"));
    }
}
