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

@Component
public class HttpRagClient implements RagClient {

    private static final Logger logger = LoggerFactory.getLogger(HttpRagClient.class);

    private final RestTemplate restTemplate;
    private final String ragUrl;
    private final ObjectMapper objectMapper;
    private final int maxRetries;

    public HttpRagClient(@Value("${qa.rag.url}") String ragUrl, RestTemplate restTemplate, ObjectMapper objectMapper,
                         @Value("${qa.rag.retries:1}") int maxRetries) {
        this.restTemplate = restTemplate;
        this.ragUrl = ragUrl;
        this.objectMapper = objectMapper;
        this.maxRetries = maxRetries;
    }

    @Override
    public AskResponse callRag(String question, String sessionId) throws Exception {
        AskRequest req = new AskRequest(question, sessionId);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<AskRequest> entity = new HttpEntity<>(req, headers);

        int attempt = 0;
        while (attempt <= maxRetries) {
            try {
                attempt++;
                AskResponse resp = restTemplate.postForObject(ragUrl, entity, AskResponse.class);
                if (resp == null) {
                    logger.warn("rag returned null on attempt {}", attempt);
                } else {
                    // record raw response if needed
                    try {
                        String raw = objectMapper.writeValueAsString(resp);
                        logger.debug("rag raw response: {}", raw);
                    } catch (Exception ex) {
                        logger.debug("failed to serialize rag response", ex);
                    }
                    return resp;
                }
            } catch (ResourceAccessException rex) {
                // typically timeout / IO
                logger.warn("rag request attempt {} failed with ResourceAccessException: {}", attempt, rex.getMessage());
            } catch (Exception ex) {
                logger.error("rag request attempt {} failed: {}", attempt, ex.getMessage());
            }

            // simple backoff
            try {
                Thread.sleep(200L * attempt);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        return null;
    }
}
