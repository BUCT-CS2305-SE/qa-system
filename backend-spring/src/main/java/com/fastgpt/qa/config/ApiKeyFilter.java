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

@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class ApiKeyFilter implements Filter {

    private static final Logger logger = LoggerFactory.getLogger(ApiKeyFilter.class);

    @Value("${qa.auth.api-key:}")
    private String requiredApiKey;

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        String path = httpRequest.getRequestURI();

        if ("OPTIONS".equalsIgnoreCase(httpRequest.getMethod())) {
            addCorsHeaders(httpRequest, httpResponse);
            httpResponse.setStatus(HttpServletResponse.SC_NO_CONTENT);
            return;
        }

        if (path.startsWith("/api/qa/health") || path.startsWith("/h2-console")) {
            chain.doFilter(request, response);
            return;
        }

        if (!path.startsWith("/api/")) {
            chain.doFilter(request, response);
            return;
        }

        if (requiredApiKey != null && !requiredApiKey.isEmpty()) {
            String apiKey = httpRequest.getHeader("X-Api-Key");
            if (!requiredApiKey.equals(apiKey)) {
                logger.warn("unauthorized request (missing X-Api-Key) from {} to {}",
                        httpRequest.getRemoteAddr(), path);
                reject(httpResponse, "未授权访问");
                return;
            }
        }

        if (path.startsWith("/api/qa/")) {
            String auth = httpRequest.getHeader("Authorization");
            if (auth == null || !auth.startsWith("Bearer ") || auth.length() < 20) {
                logger.warn("unauthorized request (missing Authorization) from {} to {}",
                        httpRequest.getRemoteAddr(), path);
                reject(httpResponse, "缺少用户凭证，请通过Web端登录后访问");
                return;
            }
        }

        chain.doFilter(request, response);
    }

    private void reject(HttpServletResponse resp, String msg) throws IOException {
        addCorsHeaders(null, resp);
        resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write("{\"code\":401,\"message\":\"" + msg + "\"}");
    }

    private void addCorsHeaders(HttpServletRequest req, HttpServletResponse resp) {
        String origin = (req != null) ? req.getHeader("Origin") : null;
        if (origin != null && !origin.isBlank()) {
            resp.setHeader("Access-Control-Allow-Origin", origin);
            resp.setHeader("Vary", "Origin");
        } else {
            resp.setHeader("Access-Control-Allow-Origin", "*");
        }
        resp.setHeader("Access-Control-Allow-Credentials", "true");
        resp.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "*");
        resp.setHeader("Access-Control-Max-Age", "3600");
    }
}
