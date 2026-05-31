package com.fastgpt.qa.controller;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.dto.HistoryDto;
import com.fastgpt.qa.model.HistoryEntity;
import com.fastgpt.qa.service.HistoryService;
import com.fastgpt.qa.service.QaService;
import com.fastgpt.qa.service.RagClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/qa")
public class QaController {

    private static final Logger logger = LoggerFactory.getLogger(QaController.class);

    private final QaService qaService;
    private final HistoryService historyService;
    private final RagClient ragClient;

    public QaController(QaService qaService, HistoryService historyService, RagClient ragClient) {
        this.qaService = qaService;
        this.historyService = historyService;
        this.ragClient = ragClient;
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

            Map<String, Object> result = ragClient.sendFeedback(traceId, helpful, comment);
            return ResponseEntity.ok(result);
        } catch (Exception ex) {
            logger.error("feedback proxy failed: {}", ex.getMessage());
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

    @GetMapping("/history")
    public ResponseEntity<List<HistoryDto>> history(
            @RequestParam(name = "sessionId", required = false) String sessionId,
            @RequestParam(name = "limit", defaultValue = "20") int limit
    ) {
        if (sessionId == null || sessionId.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        List<HistoryEntity> list = historyService.listBySession(sessionId, limit);
        List<HistoryDto> dtoList = list.stream().map(e -> {
            HistoryDto d = new HistoryDto();
            d.setId(e.getId());
            d.setRequestId(e.getRequestId());
            d.setSessionId(e.getSessionId());
            d.setQuestion(e.getQuestion());
            d.setAnswer(e.getAnswer());
            d.setNoData(e.isNoData());
            d.setSources(e.getSources());
            d.setFacts(e.getFacts());
            d.setIntent(e.getIntent());
            d.setStatus(e.getStatus());
            d.setConfidence(e.getConfidence());
            d.setCreatedAt(e.getCreatedAt());
            return d;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(dtoList);
    }
}
