package main.kotlin.com.merilo.api

import main.kotlin.com.merilo.dto.UpdatePaymentMethodsRequest
import main.kotlin.com.merilo.dto.UserResponse
import main.kotlin.com.merilo.service.UserService
import org.slf4j.LoggerFactory
import org.springframework.web.bind.annotation.*
import org.springframework.security.core.annotation.AuthenticationPrincipal
import jakarta.validation.Valid




@RestController
@RequestMapping("/api/v1/users")
class UserController(private val userService: UserService) {


    private val log = LoggerFactory.getLogger(UserController::class.java)

    @GetMapping("/me")
    fun me(@AuthenticationPrincipal principal: String): UserResponse {
        val userId = principal.toLong()
        return userService.getMe(userId)
    }

    @PatchMapping("/me/payment-methods")
    fun updatePaymentMethods(
        @AuthenticationPrincipal principal: String,
        @RequestBody @Valid body: UpdatePaymentMethodsRequest
    ): UserResponse {
        val userId = principal.toLong()
        return userService.mergePaymentMethods(userId, body.payment_methods)
    }


}