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

        // Ensure CORS preflight can succeed even when API key auth is enabled.
        // NOTE: CORS headers are normally added by Spring MVC CorsConfig, but the browser preflight may be
        // blocked earlier by this filter if we don't allow OPTIONS or return CORS headers.
        if ("OPTIONS".equalsIgnoreCase(httpRequest.getMethod())) {
            addCorsHeadersIfPresent(httpRequest, httpResponse);
            httpResponse.setStatus(HttpServletResponse.SC_NO_CONTENT);
            return;
        }

        if (requiredApiKey == null || requiredApiKey.isEmpty()) {
            chain.doFilter(request, response);
            return;
        }

        String path = httpRequest.getRequestURI();
        if (path.startsWith("/api/qa/health")) {
            chain.doFilter(request, response);
            return;
        }

        String apiKey = httpRequest.getHeader("X-Api-Key");
        if (!requiredApiKey.equals(apiKey)) {
            logger.warn("unauthorized request from {}:{} to {}",
                    httpRequest.getRemoteAddr(), httpRequest.getRemotePort(), path);

            addCorsHeadersIfPresent(httpRequest, httpResponse);
            httpResponse.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            httpResponse.setContentType("application/json;charset=UTF-8");
            httpResponse.getWriter().write("{\"code\":401,\"message\":\"未授权访问\"}");
            return;
        }

        chain.doFilter(request, response);
    }

    private void addCorsHeadersIfPresent(HttpServletRequest req, HttpServletResponse resp) {
        String origin = req.getHeader("Origin");
        if (origin == null || origin.isBlank()) {
            return;
        }
        // align to CorsConfig allowedOrigins
        if (!origin.equals("http://localhost:5173") && !origin.equals("http://127.0.0.1:5173")) {
            return;
        }
        resp.setHeader("Access-Control-Allow-Origin", origin);
        resp.setHeader("Vary", "Origin");
        resp.setHeader("Access-Control-Allow-Credentials", "true");
        resp.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
        resp.setHeader("Access-Control-Allow-Headers", "*");
        resp.setHeader("Access-Control-Max-Age", "3600");
    }
}
