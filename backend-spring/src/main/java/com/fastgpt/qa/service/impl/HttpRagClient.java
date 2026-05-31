package com.fastgpt.qa.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.RagClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class HttpRagClient implements RagClient {

    private static final Logger logger = LoggerFactory.getLogger(HttpRagClient.class);

    private final RestTemplate restTemplate;
    private final String ragAskUrl;
    private final String ragFeedbackUrl;
    private final String ragSummaryUrl;
    private final ObjectMapper objectMapper;
    private final int maxRetries;

    public HttpRagClient(RestTemplate restTemplate,
                         @Value("${qa.rag.ask-url}") String ragAskUrl,
                         @Value("${qa.rag.feedback-url}") String ragFeedbackUrl,
                         @Value("${qa.rag.summary-url}") String ragSummaryUrl,
                         ObjectMapper objectMapper,
                         @Value("${qa.rag.retries:1}") int maxRetries) {
        this.restTemplate = restTemplate;
        this.ragAskUrl = ragAskUrl;
        this.ragFeedbackUrl = ragFeedbackUrl;
        this.ragSummaryUrl = ragSummaryUrl;
        this.objectMapper = objectMapper;
        this.maxRetries = maxRetries;
    }

    @Override
    public AskResponse callRag(String question, String sessionId, String mode) throws Exception {
        AskRequest req = new AskRequest(question, sessionId, mode);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<AskRequest> entity = new HttpEntity<>(req, headers);

        int attempt = 0;
        while (attempt <= maxRetries) {
            try {
                attempt++;
                AskResponse resp = restTemplate.postForObject(ragAskUrl, entity, AskResponse.class);
                if (resp == null) {
                    logger.warn("rag returned null on attempt {}", attempt);
                } else {
                    if (logger.isDebugEnabled()) {
                        logger.debug("rag raw response: {}", objectMapper.writeValueAsString(resp));
                    }
                    return resp;
                }
            } catch (ResourceAccessException rex) {
                logger.warn("rag ask attempt {} failed: {}", attempt, rex.getMessage());
            } catch (Exception ex) {
                logger.error("rag ask attempt {} failed: {}", attempt, ex.getMessage());
            }

            try {
                Thread.sleep(200L * attempt);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        return null;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> sendFeedback(String traceId, boolean helpful, String comment) throws Exception {
        Map<String, Object> body = new java.util.HashMap<>();
        body.put("trace_id", traceId);
        body.put("helpful", helpful);
        body.put("comment", comment);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        return restTemplate.postForObject(ragFeedbackUrl, entity, Map.class);
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> getSummary() throws Exception {
        return restTemplate.getForObject(ragSummaryUrl, Map.class);
    }
}
