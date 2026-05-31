package com.fastgpt.qa.controller;

import com.fastgpt.qa.dto.HistoryDto;
import com.fastgpt.qa.model.HistoryEntity;
import com.fastgpt.qa.service.HistoryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/qa/history")
public class HistoryController {

    private final HistoryService historyService;

    public HistoryController(HistoryService historyService) {
        this.historyService = historyService;
    }

    @GetMapping("/list")
    public ResponseEntity<List<HistoryDto>> list(@RequestParam String sessionId,
                                                 @RequestParam(defaultValue = "20") int limit) {
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

    @GetMapping("/{id}")
    public ResponseEntity<HistoryDto> get(@PathVariable Long id) {
        Optional<HistoryEntity> opt = historyService.getById(id);
        if (opt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        HistoryEntity e = opt.get();
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
        return ResponseEntity.ok(d);
    }
}
