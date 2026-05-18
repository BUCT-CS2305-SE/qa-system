package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;

public interface QaService {
    AskResponse ask(AskRequest request);
}
