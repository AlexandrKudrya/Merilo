package com.merilo.common.exception

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice



@RestControllerAdvice
class ApiExceptionHandler {

    data class ErrorResponse(val message: String)

    @ExceptionHandler(IllegalArgumentException::class)
    fun handleBadRequest(e: IllegalArgumentException): ResponseEntity<ErrorResponse> {
        val msg = e.message ?: "bad request"


        val status = if (
            msg.contains("signature", ignoreCase = true) ||
            msg.contains("too old", ignoreCase = true)
        ) HttpStatus.UNAUTHORIZED else HttpStatus.BAD_REQUEST

        return ResponseEntity.status(status).body(ErrorResponse(msg))
    }
}