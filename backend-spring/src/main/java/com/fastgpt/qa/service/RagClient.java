package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskResponse;

import java.util.Map;

public interface RagClient {
    AskResponse callRag(String question, String sessionId, String mode) throws Exception;

    AskResponse callRag(String question, String sessionId, String mode, String kgToken) throws Exception;

    Map<String, Object> sendFeedback(String traceId, boolean helpful, String comment) throws Exception;

    Map<String, Object> getSummary() throws Exception;
}
