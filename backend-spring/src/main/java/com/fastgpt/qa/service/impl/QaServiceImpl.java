package com.fastgpt.qa.service.impl;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.QaService;
import com.fastgpt.qa.service.HistoryService;
import com.fastgpt.qa.service.RagClient;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.slf4j.MDC;

import java.time.Duration;

@Service
public class QaServiceImpl implements QaService {

    private static final Logger logger = LoggerFactory.getLogger(QaServiceImpl.class);

    private final RagClient ragClient;
    private final HistoryService historyService;
    private final MeterRegistry meterRegistry;

    public QaServiceImpl(RagClient ragClient, HistoryService historyService, MeterRegistry meterRegistry) {
        this.ragClient = ragClient;
        this.historyService = historyService;
        this.meterRegistry = meterRegistry;
    }

    @Override
    public AskResponse ask(AskRequest request) {
        long start = System.nanoTime();

        String question = request.getQuestion();
        if (question == null || question.trim().isEmpty()) {
            AskResponse resp = new AskResponse();
            resp.setStatus("no_data");
            resp.setCode(2001);
            resp.setAnswer("暂无相关数据");
            resp.setTraceId("N/A");
            historyService.save(request, resp);
            return resp;
        }

        try {
            Timer.Sample sample = Timer.start(meterRegistry);
            AskResponse resp = ragClient.callRag(question, request.getSessionId(), request.getMode());
            sample.stop(meterRegistry.timer("qa.rag.call.duration"));

            if (resp != null) {
                MDC.put("traceId", resp.getTraceId());
                historyService.save(request, resp);
                meterRegistry.counter("qa.responses", "type", resp.getStatus() != null ? resp.getStatus() : "ok").increment();
                MDC.clear();
                return resp;
            }
        } catch (Exception ex) {
            logger.error("error calling rag: {}", ex.getMessage());
            meterRegistry.counter("qa.errors", "stage", "rag_call").increment();
        }

        AskResponse fallback = new AskResponse();
        fallback.setStatus("no_data");
        fallback.setCode(5004);
        fallback.setAnswer("问答服务暂时不可用，请稍后重试。");
        fallback.setTraceId("N/A");
        historyService.save(request, fallback);
        meterRegistry.counter("qa.responses", "type", "error").increment();
        Timer.builder("qa.request.duration").register(meterRegistry).record(Duration.ofNanos(System.nanoTime() - start));
        return fallback;
    }
}
