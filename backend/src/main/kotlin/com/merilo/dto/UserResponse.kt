package main.kotlin.com.merilo.dto


data class UserResponse(
    val id: Long,
    val telegram_id: Long?,
    val username: String?,
    val payment_methods: Map<String, String>
)