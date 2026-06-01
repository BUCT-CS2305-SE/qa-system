package com.fastgpt.qa.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class AskResponse {

    // --- new SRS-aligned fields ---

    @JsonProperty("request_id")
    private String requestId;

    @JsonProperty("no_data")
    private boolean noData;

    @JsonProperty("sources")
    private List<Source> sources = new ArrayList<>();

    @JsonProperty("source")
    private Source sourceItem;

    // --- backward-compatible diagnostics fields ---

    private String status;
    private int code;
    private String intent;
    private String answer;
    private List<Fact> facts = new ArrayList<>();

    @JsonProperty("llm_note")
    private String llmNote;
    private double confidence;

    @JsonProperty("trace_id")
    private String traceId;

    // --- inner classes ---

    public static class Source {
        @JsonProperty("source_name")
        private String sourceName;

        @JsonProperty("detail_url")
        private String detailUrl;

        public Source() {}

        public Source(String sourceName, String detailUrl) {
            this.sourceName = sourceName;
            this.detailUrl = detailUrl;
        }

        public String getSourceName() {
            return sourceName;
        }

        public void setSourceName(String sourceName) {
            this.sourceName = sourceName;
        }

        public String getDetailUrl() {
            return detailUrl;
        }

        public void setDetailUrl(String detailUrl) {
            this.detailUrl = detailUrl;
        }
    }

    public static class Fact {
        private String subject;
        private String predicate;
        private String object;

        @JsonProperty("source_name")
        private String sourceName;

        @JsonProperty("source_url")
        private String sourceUrl;

        public Fact() {}

        public Fact(String subject, String predicate, String object) {
            this.subject = subject;
            this.predicate = predicate;
            this.object = object;
        }

        public String getSubject() {
            return subject;
        }

        public void setSubject(String subject) {
            this.subject = subject;
        }

        public String getPredicate() {
            return predicate;
        }

        public void setPredicate(String predicate) {
            this.predicate = predicate;
        }

        public String getObject() {
            return object;
        }

        public void setObject(String object) {
            this.object = object;
        }

        public String getSourceName() {
            return sourceName;
        }

        public void setSourceName(String sourceName) {
            this.sourceName = sourceName;
        }

        public String getSourceUrl() {
            return sourceUrl;
        }

        public void setSourceUrl(String sourceUrl) {
            this.sourceUrl = sourceUrl;
        }
    }

    // --- constructors ---

    public AskResponse() {}

    // --- convenient methods ---

    public boolean isNoData() {
        return noData || "no_data".equals(status) || status == null;
    }

    /**
     * Returns the source list for backward compatibility.
     * Prefers the new {@code sources} array; falls back to wrapping {@code sourceItem}.
     */
    @JsonIgnore
    public List<Source> getSource() {
        if (sources != null && !sources.isEmpty()) {
            return sources;
        }
        if (sourceItem != null) {
            return Collections.singletonList(sourceItem);
        }
        return new ArrayList<>();
    }

    // --- accessors ---

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public boolean getNoData() {
        return noData;
    }

    public void setNoData(boolean noData) {
        this.noData = noData;
    }

    public List<Source> getSources() {
        return sources;
    }

    public void setSources(List<Source> sources) {
        this.sources = sources;
    }

    public Source getSourceItem() {
        return sourceItem;
    }

    public void setSourceItem(Source sourceItem) {
        this.sourceItem = sourceItem;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getIntent() {
        return intent;
    }

    public void setIntent(String intent) {
        this.intent = intent;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<Fact> getFacts() {
        return facts;
    }

    public void setFacts(List<Fact> facts) {
        this.facts = facts;
    }

    public String getLlmNote() {
        return llmNote;
    }

    public void setLlmNote(String llmNote) {
        this.llmNote = llmNote;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }
}
