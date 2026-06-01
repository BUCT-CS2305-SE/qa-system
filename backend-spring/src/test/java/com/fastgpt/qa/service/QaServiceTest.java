package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.impl.QaServiceImpl;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class QaServiceTest {

    @Mock
    private RagClient ragClient;

    @Mock
    private HistoryService historyService;

    private MeterRegistry meterRegistry;
    private QaServiceImpl qaService;

    @BeforeEach
    void setUp() {
        meterRegistry = new SimpleMeterRegistry();
        qaService = new QaServiceImpl(ragClient, historyService, meterRegistry);
    }

    @Test
    void shouldReturnNoDataWhenQuestionIsEmpty() throws Exception {
        AskRequest request = new AskRequest("", "sess-1");

        AskResponse resp = qaService.ask(request);

        assertNotNull(resp);
        assertEquals("no_data", resp.getStatus());
        assertEquals(2001, resp.getCode());
        assertTrue(resp.getAnswer().contains("暂无相关数据"));
        verify(ragClient, never()).callRag(anyString(), anyString(), anyString());
    }

    @Test
    void shouldReturnNoDataWhenQuestionIsNull() throws Exception {
        AskRequest request = new AskRequest(null, "sess-1");

        AskResponse resp = qaService.ask(request);

        assertNotNull(resp);
        assertEquals("no_data", resp.getStatus());
        assertEquals(2001, resp.getCode());
    }

    @Test
    void shouldReturnFallbackWhenRagReturnsNull() throws Exception {
        when(ragClient.callRag(anyString(), anyString(), anyString())).thenReturn(null);

        AskRequest request = new AskRequest("什么是女史箴图？", "sess-1");
        AskResponse resp = qaService.ask(request);

        assertNotNull(resp);
        assertEquals("no_data", resp.getStatus());
        assertEquals(5004, resp.getCode());
        assertTrue(resp.getAnswer().contains("暂时不可用"));
        verify(historyService).save(eq(request), any(AskResponse.class));
    }

    @Test
    void shouldReturnFallbackWhenRagThrowsException() throws Exception {
        when(ragClient.callRag(anyString(), anyString(), anyString()))
                .thenThrow(new RuntimeException("RAG service down"));

        AskRequest request = new AskRequest("什么是女史箴图？", "sess-1");
        AskResponse resp = qaService.ask(request);

        assertNotNull(resp);
        assertEquals("no_data", resp.getStatus());
        assertEquals(5004, resp.getCode());
    }

    @Test
    void shouldReturnRagResponseWhenSuccessful() throws Exception {
        AskResponse mockResp = new AskResponse();
        mockResp.setRequestId("req-ok");
        mockResp.setAnswer("女史箴图现藏于大英博物馆");
        mockResp.setStatus("ok");
        mockResp.setCode(0);
        mockResp.setIntent("artifact_museum");
        mockResp.setTraceId("trace-1");

        when(ragClient.callRag(anyString(), anyString(), anyString())).thenReturn(mockResp);

        AskRequest request = new AskRequest("女史箴图在哪个博物馆？", "sess-1");
        AskResponse resp = qaService.ask(request);

        assertNotNull(resp);
        assertEquals("ok", resp.getStatus());
        assertEquals("artifact_museum", resp.getIntent());
        assertEquals("女史箴图现藏于大英博物馆", resp.getAnswer());
        verify(historyService).save(eq(request), eq(mockResp));
    }

    @Test
    void shouldPassSessionIdToRagClient() throws Exception {
        AskResponse mockResp = new AskResponse();
        mockResp.setStatus("ok");
        when(ragClient.callRag(anyString(), anyString(), anyString())).thenReturn(mockResp);

        AskRequest request = new AskRequest("test", "sess-abc", "rule");
        qaService.ask(request);

        verify(ragClient).callRag("test", "sess-abc", "rule");
    }
}
