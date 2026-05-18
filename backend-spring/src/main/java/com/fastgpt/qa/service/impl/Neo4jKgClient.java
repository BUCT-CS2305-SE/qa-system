package com.fastgpt.qa.service.impl;

import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.KgClient;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class Neo4jKgClient implements KgClient {

    @Override
    public List<AskResponse.Fact> queryFacts(String question) {
        // 占位实现：基于关键字简单匹配，后续替换为 Neo4j driver 调用
        List<AskResponse.Fact> facts = new ArrayList<>();
        if (question.contains("年代") || question.contains("朝代")) {
            facts.add(new AskResponse.Fact("朝代", "唐代"));
        }
        return facts;
    }
}
