package com.fastgpt.qa.service.impl;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.QaService;
import com.fastgpt.qa.service.HistoryService;
import com.fastgpt.qa.service.RagClient;
import com.fastgpt.qa.service.KgClient;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.slf4j.MDC;

import java.time.Duration;
import java.util.List;
import java.util.UUID;

@Service
public class QaServiceImpl implements QaService {

    private static final Logger logger = LoggerFactory.getLogger(QaServiceImpl.class);

    private final RagClient ragClient;
    private final HistoryService historyService;
    private final MeterRegistry meterRegistry;
    private final KgClient kgClient;

    public QaServiceImpl(RagClient ragClient, HistoryService historyService, MeterRegistry meterRegistry, KgClient kgClient) {
        this.ragClient = ragClient;
        this.historyService = historyService;
        this.meterRegistry = meterRegistry;
        this.kgClient = kgClient;
    }

    @Override
    public AskResponse ask(AskRequest request) {
        long start = System.nanoTime();
        AskResponse resp = new AskResponse();
        resp.setRequestId(UUID.randomUUID().toString());

        // put in MDC
        MDC.put("requestId", resp.getRequestId());

        String question = request.getQuestion();
        if (question == null || question.trim().isEmpty()) {
            resp.setNoData(true);
            resp.setAnswer("暂无相关数据");
            // save history
            historyService.save(request, resp);
            MDC.clear();
            return resp;
        }

        // 1) try KG
        try {
            long kgStart = System.nanoTime();
            List<AskResponse.Fact> facts = kgClient.queryFacts(question);
            long kgEnd = System.nanoTime();
            if (!facts.isEmpty()) {
                resp.setNoData(false);
                resp.setAnswer("KG 命中，返回结构化 facts");
                resp.setFacts(facts);
                resp.getSources().add(new AskResponse.Source("KG", ""));
                historyService.save(request, resp);
                meterRegistry.counter("qa.responses", "type", "kg").increment();
                Timer.builder("qa.kg.duration").register(meterRegistry).record(Duration.ofNanos(kgEnd - kgStart));
                MDC.clear();
                return resp;
            }
        } catch (Exception ex) {
            logger.warn("kg query failed: {}", ex.getMessage());
            meterRegistry.counter("qa.errors", "stage", "kg").increment();
        }

        // 2) call RAG
        try {
            Timer.Sample sample = Timer.start(meterRegistry);
            AskResponse ragResp = ragClient.callRag(request.getQuestion(), request.getSessionId());
            sample.stop(meterRegistry.timer("qa.rag.call.duration"));

            if (ragResp != null && !ragResp.isNoData()) {
                ragResp.setRequestId(resp.getRequestId());
                historyService.save(request, ragResp);
                meterRegistry.counter("qa.responses", "type", "rag").increment();
                MDC.clear();
                return ragResp;
            }
        } catch (Exception ex) {
            logger.error("error calling rag: {}", ex.getMessage());
            meterRegistry.counter("qa.errors", "stage", "rag_call").increment();
        }

        // fallback mock logic
        if (question.contains("年代") || question.contains("朝代")) {
            resp.setAnswer("根据知识库，文物A约属唐代。");
            resp.setNoData(false);
            AskResponse.Fact f = new AskResponse.Fact("朝代", "唐代");
            resp.getFacts().add(f);
            AskResponse.Source s = new AskResponse.Source("示例博物馆", "https://example.org/artifact/1");
            resp.getSources().add(s);
            historyService.save(request, resp);
            meterRegistry.counter("qa.responses", "type", "mock").increment();
            MDC.clear();
            return resp;
        }

        resp.setAnswer("暂无相关数据");
        resp.setNoData(true);
        historyService.save(request, resp);
        meterRegistry.counter("qa.responses", "type", "no_data").increment();
        MDC.clear();
        long end = System.nanoTime();
        Timer.builder("qa.request.duration").register(meterRegistry).record(Duration.ofNanos(end - start));
        return resp;
    }
}
