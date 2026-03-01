package main.kotlin.com.merilo.integration.telegram

import com.fasterxml.jackson.annotation.JsonProperty

data class TelegramUser(
    val id: Long,
    val username: String? = null,
    @JsonProperty("first_name")
    val firstName: String? = null,
    @JsonProperty("last_name")
    val lastName: String? = null
)