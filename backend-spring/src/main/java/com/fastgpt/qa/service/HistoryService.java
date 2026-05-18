package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.model.HistoryEntity;

import java.util.List;
import java.util.Optional;

public interface HistoryService {
    HistoryEntity save(AskRequest req, AskResponse resp);
    List<HistoryEntity> listBySession(String sessionId, int limit);
    Optional<HistoryEntity> getById(Long id);
}
