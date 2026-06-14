package com.fastgpt.qa.config;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedDeque;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 20)
public class RateLimitFilter implements Filter {

    private static final Logger logger = LoggerFactory.getLogger(RateLimitFilter.class);

    @Value("${qa.rate-limit.max-requests:60}")
    private int maxRequests;

    @Value("${qa.rate-limit.window-seconds:60}")
    private int windowSeconds;

    private final Map<String, Deque<Long>> requestTimestamps = new ConcurrentHashMap<>();

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        String path = httpRequest.getRequestURI();
        if ((!path.startsWith("/api/qa/") && !path.startsWith("/api/v1/")) || path.startsWith("/api/qa/health")) {
            chain.doFilter(request, response);
            return;
        }

        String clientIp = httpRequest.getRemoteAddr();
        long now = System.currentTimeMillis();
        long windowStart = now - (windowSeconds * 1000L);

        Deque<Long> timestamps = requestTimestamps.computeIfAbsent(clientIp, k -> new ConcurrentLinkedDeque<>());

        synchronized (timestamps) {
            while (!timestamps.isEmpty() && timestamps.peekFirst() < windowStart) {
                timestamps.pollFirst();
            }

            int requestCount = timestamps.size();
            httpResponse.setHeader("X-RateLimit-Remaining",
                String.valueOf(Math.max(0, maxRequests - requestCount - 1)));
            httpResponse.setHeader("X-RateLimit-Limit", String.valueOf(maxRequests));

            if (requestCount >= maxRequests) {
                logger.warn("rate limit exceeded for {} ({} requests in {}s)",
                    clientIp, requestCount, windowSeconds);
                httpResponse.setStatus(429);
                httpResponse.setContentType("application/json;charset=UTF-8");
                httpResponse.getWriter().write(
                    "{\"code\":429,\"message\":\"请求过于频繁，请稍后重试\"}");
                return;
            }

            timestamps.addLast(now);
        }

        chain.doFilter(request, response);
    }
}
