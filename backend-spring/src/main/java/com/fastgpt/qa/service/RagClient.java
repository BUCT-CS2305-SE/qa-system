package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskResponse;

public interface RagClient {
    AskResponse callRag(String question, String sessionId) throws Exception;
}
