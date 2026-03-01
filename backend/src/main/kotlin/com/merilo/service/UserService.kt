package main.kotlin.com.merilo.service

import jakarta.transaction.Transactional
import main.kotlin.com.merilo.dto.UserResponse
import main.kotlin.com.merilo.model.UserEntity
import main.kotlin.com.merilo.repository.UserRepository
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Service
import org.springframework.web.server.ResponseStatusException

@Service
class UserService(
    private val userRepository: UserRepository,
) {
    private val log = LoggerFactory.getLogger(UserService::class.java)

    fun getMe(userId: Long): UserResponse {
        log.info("Getting me $userId")
        val user = userRepository.findById(userId)
        .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND) }

        return user.toDto()
    }

    @Transactional
    fun mergePaymentMethods(userId: Long, patch: Map<String,String>): UserResponse {
        val user = userRepository.findById(userId)
        .orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND) }

        user.paymentMethods = user.paymentMethods.plus(patch)
        return user.toDto()
    }

    private fun UserEntity.toDto() = UserResponse (
        id = requireNotNull(id),
        telegram_id = telegramId,
        username = username,
        payment_methods = paymentMethods
    )
}