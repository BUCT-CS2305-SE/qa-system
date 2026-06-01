package com.fastgpt.qa.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class AskRequest {
    @NotBlank
    @Size(max = 500, message = "问题长度不能超过500字符")
    private String question;

    @JsonProperty("session_id")
    private String sessionId;

    private String mode = "auto";

    public AskRequest() {
    }

    public AskRequest(String question, String sessionId) {
        this.question = question;
        this.sessionId = sessionId;
    }

    public AskRequest(String question, String sessionId, String mode) {
        this.question = question;
        this.sessionId = sessionId;
        this.mode = mode;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }
}
