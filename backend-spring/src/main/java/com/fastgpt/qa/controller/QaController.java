package com.fastgpt.qa.controller;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.model.FeedbackEntity;
import com.fastgpt.qa.repository.FeedbackRepository;
import com.fastgpt.qa.service.QaService;
import com.fastgpt.qa.service.RagClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/qa")
public class QaController {

    private static final Logger logger = LoggerFactory.getLogger(QaController.class);

    private final QaService qaService;
    private final RagClient ragClient;
    private final FeedbackRepository feedbackRepository;

    public QaController(QaService qaService, RagClient ragClient,
                        FeedbackRepository feedbackRepository) {
        this.qaService = qaService;
        this.ragClient = ragClient;
        this.feedbackRepository = feedbackRepository;
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("ok");
    }

    @PostMapping("/ask")
    public ResponseEntity<AskResponse> ask(@Validated @RequestBody AskRequest request) {
        AskResponse resp = qaService.ask(request);
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/feedback")
    public ResponseEntity<Map<String, Object>> feedback(@RequestBody Map<String, Object> payload) {
        try {
            String traceId = (String) payload.get("trace_id");
            boolean helpful = Boolean.TRUE.equals(payload.get("helpful"));
            String comment = (String) payload.get("comment");

            feedbackRepository.save(new FeedbackEntity(traceId, helpful, comment));

            Map<String, Object> result = ragClient.sendFeedback(traceId, helpful, comment);
            return ResponseEntity.ok(result);
        } catch (Exception ex) {
            logger.error("feedback proxy failed: {}", ex.getMessage());

            try {
                String traceId = (String) payload.get("trace_id");
                boolean helpful = Boolean.TRUE.equals(payload.get("helpful"));
                String comment = (String) payload.get("comment");
                feedbackRepository.save(new FeedbackEntity(traceId, helpful, comment));
            } catch (Exception ignored) {}

            Map<String, Object> err = Map.of("status", "error", "code", 5004, "message", "反馈提交失败");
            return ResponseEntity.internalServerError().body(err);
        }
    }

    @GetMapping("/summary")
    public ResponseEntity<Map<String, Object>> summary() {
        try {
            Map<String, Object> result = ragClient.getSummary();
            return ResponseEntity.ok(result);
        } catch (Exception ex) {
            logger.error("summary proxy failed: {}", ex.getMessage());
            Map<String, Object> err = Map.of("status", "error", "code", 5004, "message", "获取统计失败");
            return ResponseEntity.internalServerError().body(err);
        }
    }
}
