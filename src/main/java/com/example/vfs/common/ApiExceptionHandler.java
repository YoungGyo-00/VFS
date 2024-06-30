package com.example.vfs.common;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

@Slf4j
@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ApiResponse<?>> handleNoResourceFoundException(NoResourceFoundException exception) {
        // NoResourceFoundException이 발생했을 때 아무런 처리도 하지 않음
        return ResponseEntity.ok().build();
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<?>> handleExceptions(Exception exception) {
        log.error("Exception occurred:", exception); // 스택 트레이스 정보를 포함한 로깅

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(ApiResponse.errorResponse(exception.getMessage()));
    }
}
