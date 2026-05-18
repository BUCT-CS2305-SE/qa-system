package com.fastgpt.qa.service;

import com.fastgpt.qa.dto.AskResponse;

import java.util.List;

public interface KgClient {
    /**
     * Query KG by question or parameters and return facts (may be empty)
     */
    List<AskResponse.Fact> queryFacts(String question);
}
