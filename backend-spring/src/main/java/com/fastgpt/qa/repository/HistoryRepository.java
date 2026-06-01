package com.fastgpt.qa.repository;

import com.fastgpt.qa.model.HistoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface HistoryRepository extends JpaRepository<HistoryEntity, Long> {
    List<HistoryEntity> findBySessionIdOrderByCreatedAtDesc(String sessionId);

    long deleteByCreatedAtBefore(LocalDateTime cutoff);

    long countByCreatedAtBefore(LocalDateTime cutoff);
}
