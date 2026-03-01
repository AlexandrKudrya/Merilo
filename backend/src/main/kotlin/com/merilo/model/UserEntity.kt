package main.kotlin.com.merilo.model

import com.vladmihalcea.hibernate.type.json.JsonType
import org.hibernate.annotations.Type
import jakarta.persistence.*
import org.hibernate.annotations.CreationTimestamp
import java.time.OffsetDateTime

@Entity
@Table(name = "users")
class UserEntity(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "telegram_id", unique = true, nullable = false)
    val telegramId: Long,

    @Column(name = "username")
    var username: String? = null,

    @Type(JsonType::class)
    @Column(name = "payment_methods", columnDefinition = "jsonb", nullable = false)
    var paymentMethods: Map<String, String> = emptyMap(),

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: OffsetDateTime? = null
)