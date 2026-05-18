package com.fastgpt.qa.service.impl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.model.HistoryEntity;
import com.fastgpt.qa.repository.HistoryRepository;
import com.fastgpt.qa.service.HistoryService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class HistoryServiceImpl implements HistoryService {

    private final HistoryRepository historyRepository;
    private final ObjectMapper objectMapper;

    public HistoryServiceImpl(HistoryRepository historyRepository, ObjectMapper objectMapper) {
        this.historyRepository = historyRepository;
        this.objectMapper = objectMapper;
    }

    @Override
    public HistoryEntity save(AskRequest req, AskResponse resp) {
        HistoryEntity e = new HistoryEntity();
        e.setRequestId(resp.getRequestId());
        e.setSessionId(req.getSessionId());
        e.setQuestion(req.getQuestion());
        e.setAnswer(resp.getAnswer());
        e.setNoData(resp.isNoData());
        try {
            e.setSources(objectMapper.writeValueAsString(resp.getSources()));
            e.setFacts(objectMapper.writeValueAsString(resp.getFacts()));
            e.setRawResponse(objectMapper.writeValueAsString(resp));
        } catch (JsonProcessingException ex) {
            e.setRawResponse("{}");
        }
        e.setCreatedAt(LocalDateTime.now());
        return historyRepository.save(e);
    }

    @Override
    public List<HistoryEntity> listBySession(String sessionId, int limit) {
        List<HistoryEntity> list = historyRepository.findBySessionIdOrderByCreatedAtDesc(sessionId);
        if (list.size() > limit) {
            return list.subList(0, limit);
        }
        return list;
    }

    @Override
    public Optional<HistoryEntity> getById(Long id) {
        return historyRepository.findById(id);
    }
}
