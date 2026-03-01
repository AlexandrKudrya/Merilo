package main.kotlin.com.merilo.service



import main.kotlin.com.merilo.config.JwtService
import main.kotlin.com.merilo.dto.AuthResponse
import main.kotlin.com.merilo.integration.telegram.TelegramUser
import main.kotlin.com.merilo.model.UserEntity
import main.kotlin.com.merilo.repository.UserRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class AuthService(
    private val userRepository: UserRepository,
    private val jwtService: JwtService
) {

    @Transactional
    fun loginOrRegister(tgUser: TelegramUser): AuthResponse {
        val existing = userRepository.findByTelegramId(tgUser.id)

        val user = if (existing != null) {

            if (tgUser.username != null && tgUser.username != existing.username) {
                existing.username = tgUser.username
            }
            existing
        } else {
            userRepository.save(
                UserEntity(
                    telegramId = tgUser.id,
                    username = tgUser.username
                )
            )
        }

        val token = jwtService.generateToken(user.id!!)
        return AuthResponse(access_token = token)
    }
}