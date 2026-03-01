package main.kotlin.com.merilo.dto

data class AuthResponse(
    val access_token: String,
    val token_type: String = "bearer"
)