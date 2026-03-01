package main.kotlin.com.merilo.dto


import org.jetbrains.annotations.NotNull

data class UpdatePaymentMethodsRequest (
    @field:NotNull
    val payment_methods: Map<String, String>
)