package com.fastgpt.qa.controller;

import com.fastgpt.qa.dto.AskRequest;
import com.fastgpt.qa.dto.AskResponse;
import com.fastgpt.qa.service.QaService;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ExternalApiController {

    private final QaService qaService;

    public ExternalApiController(QaService qaService) {
        this.qaService = qaService;
    }

    @PostMapping("/ask")
    public ResponseEntity<AskResponse> ask(@Validated @RequestBody AskRequest request) {
        AskResponse resp = qaService.ask(request);
        return ResponseEntity.ok(resp);
    }
}
