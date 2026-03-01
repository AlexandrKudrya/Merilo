package main.kotlin.com.merilo.config

import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.Keys
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import java.nio.charset.StandardCharsets
import java.util.Date

@Component
class JwtService(
    @param:Value("\${jwt.secret}") private val secret: String,
    @param:Value("\${jwt.expiration-minutes}") private val expirationMinutes: Long
) {

    private val key = Keys.hmacShaKeyFor(secret.toByteArray(StandardCharsets.UTF_8))

    fun generateToken(userId: Long): String {
        val now = Date()
        val expirationDate = Date(now.time + expirationMinutes*60_000)

        return Jwts.builder()
            .subject(userId.toString())
            .issuedAt(now)
            .expiration(expirationDate)
            .signWith(key)
            .compact()
    }

    fun parseUserId(token: String): Long {
        val claims = Jwts.parser()
            .verifyWith(key)
            .build()
            .parseSignedClaims(token)
            .payload

        return claims.subject.toLong()
    }
}