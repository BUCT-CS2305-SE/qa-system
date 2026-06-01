package com.fastgpt.qa.repository;

import com.fastgpt.qa.model.FeedbackEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FeedbackRepository extends JpaRepository<FeedbackEntity, Long> {
    List<FeedbackEntity> findByHelpfulFalseOrderByCreatedAtDesc();
}
