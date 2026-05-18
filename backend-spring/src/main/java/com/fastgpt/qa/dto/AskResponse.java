package com.fastgpt.qa.dto;

import java.util.ArrayList;
import java.util.List;

public class AskResponse {
    private String requestId;
    private String answer;
    private boolean noData;
    private List<Source> sources = new ArrayList<>();
    private List<Fact> facts = new ArrayList<>();

    public static class Source {
        private String sourceName;
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
        private String key;
        private String value;

        public Fact() {}

        public Fact(String key, String value) {
            this.key = key;
            this.value = value;
        }

        public String getKey() {
            return key;
        }

        public void setKey(String key) {
            this.key = key;
        }

        public String getValue() {
            return value;
        }

        public void setValue(String value) {
            this.value = value;
        }
    }

    public AskResponse() {}

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public boolean isNoData() {
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

    public List<Fact> getFacts() {
        return facts;
    }

    public void setFacts(List<Fact> facts) {
        this.facts = facts;
    }
}
