package com.fastgpt.qa.config;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class RateLimitInterceptor implements HandlerInterceptor {

    private static final Logger logger = LoggerFactory.getLogger(RateLimitInterceptor.class);

    @Value("${qa.rate-limit.max-requests:60}")
    private int maxRequests;

    @Value("${qa.rate-limit.window-seconds:60}")
    private int windowSeconds;

    private final Map<String, WindowCounter> counters = new ConcurrentHashMap<>();

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        String path = request.getRequestURI();
        if (path.startsWith("/api/qa/health")) {
            return true;
        }

        String clientIp = request.getRemoteAddr();
        long now = System.currentTimeMillis();
        long windowStart = now - (windowSeconds * 1000L);

        WindowCounter counter = counters.compute(clientIp, (k, v) -> {
            if (v == null || v.timestamp < windowStart) {
                return new WindowCounter(now, 1);
            }
            v.count++;
            return v;
        });

        if (counter.timestamp < windowStart) {
            counter.timestamp = now;
            counter.count = 1;
            return true;
        }

        if (counter.count > maxRequests) {
            logger.warn("rate limit exceeded for {} ({} requests in {}s)", clientIp, counter.count, windowSeconds);
            response.setStatus(429);
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write("{\"code\":429,\"message\":\"请求过于频繁，请稍后重试\"}");
            return false;
        }

        return true;
    }

    private static class WindowCounter {
        long timestamp;
        int count;

        WindowCounter(long timestamp, int count) {
            this.timestamp = timestamp;
            this.count = count;
        }
    }
}
