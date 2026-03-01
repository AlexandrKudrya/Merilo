package main.kotlin.com.merilo.api

import main.kotlin.com.merilo.dto.AuthResponse
import main.kotlin.com.merilo.dto.TelegramAuthRequest
import main.kotlin.com.merilo.integration.telegram.TelegramInitDataVerifier
import main.kotlin.com.merilo.service.AuthService
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*




@RestController
@RequestMapping("/api/v1/auth")
class AuthController(
    private val verifier: TelegramInitDataVerifier,
    private val authService: AuthService
) {

    @PostMapping("/telegram")
    @ResponseStatus(HttpStatus.OK)
    fun telegramAuth(@RequestBody body: TelegramAuthRequest): AuthResponse {
        val verified = verifier.verifyAndExtract(body.init_data)
        return authService.loginOrRegister(verified.telegramUser)
    }
}