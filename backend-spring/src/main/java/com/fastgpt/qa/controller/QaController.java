package com.fastgpt.qa.controller;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.dto.HistoryDto;
import com.fastgpt.qa.model.HistoryEntity;
import com.fastgpt.qa.service.HistoryService;
import com.fastgpt.qa.service.QaService;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/qa")
public class QaController {

    private final QaService qaService;
    private final HistoryService historyService;

    public QaController(QaService qaService, HistoryService historyService) {
        this.qaService = qaService;
        this.historyService = historyService;
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
    public ResponseEntity<String> feedback(@RequestBody String payload) {
        // 暂存或打印
        System.out.println("feedback: " + payload);
        return ResponseEntity.ok("ok");
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
            d.setCreatedAt(e.getCreatedAt());
            return d;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(dtoList);
    }
}
