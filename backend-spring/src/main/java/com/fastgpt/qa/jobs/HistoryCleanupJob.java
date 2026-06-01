package com.fastgpt.qa.jobs;

import com.fastgpt.qa.repository.HistoryRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class HistoryCleanupJob {

    private static final Logger logger = LoggerFactory.getLogger(HistoryCleanupJob.class);

    private final HistoryRepository historyRepository;

    /**
     * 保留天数（默认 30 天 ≈ 按月清理）。
     */
    @Value("${qa.history.retention-days:30}")
    private int retentionDays;

    public HistoryCleanupJob(HistoryRepository historyRepository) {
        this.historyRepository = historyRepository;
    }

    /**
     * 每天凌晨 03:10 执行一次（简单可靠，比“每月某天”更抗漏跑），按 retentionDays 删除过期历史。
     */
    @Scheduled(cron = "0 10 3 * * *")
    public void cleanup() {
        if (retentionDays <= 0) {
            logger.info("History cleanup disabled (qa.history.retention-days={})", retentionDays);
            return;
        }

        LocalDateTime cutoff = LocalDateTime.now().minusDays(retentionDays);
        long pending = historyRepository.countByCreatedAtBefore(cutoff);
        if (pending <= 0) {
            return;
        }

        long deleted = historyRepository.deleteByCreatedAtBefore(cutoff);
        logger.info("History cleanup done. retentionDays={}, cutoff={}, deleted={}", retentionDays, cutoff, deleted);
    }
}
