package main.kotlin.com.merilo.integration.telegram

import com.fasterxml.jackson.databind.ObjectMapper
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import java.security.MessageDigest
import kotlin.math.abs

@Component
class TelegramInitDataVerifier(
    @Value("\${telegram.bot-token}") private val botToken: String,
    @Value("\${security.initdata-max-age-seconds:86400}") private val maxAgeSeconds: Long,
    private val objectMapper: ObjectMapper
) {

    data class VerifiedInitData(
        val telegramUser: TelegramUser,
        val authDate: Long
    )

    fun verifyAndExtract(initDataRaw: String, nowEpochSeconds: Long = System.currentTimeMillis() / 1000): VerifiedInitData {
        val params = parseQuery(initDataRaw)
        val log = LoggerFactory.getLogger(TelegramInitDataVerifier::class.java)

        val hash = params["hash"] ?: throw IllegalArgumentException("initData missing hash")
        val authDateStr = params["auth_date"] ?: throw IllegalArgumentException("initData missing auth_date")
        val userJson = params["user"] ?: throw IllegalArgumentException("initData missing user")

        val authDate = authDateStr.toLongOrNull() ?: throw IllegalArgumentException("auth_date is not a number")

        // Проверка "свежести" initData (защита от реплея)
        if (abs(nowEpochSeconds - authDate) > maxAgeSeconds) {
            throw IllegalArgumentException("initData is too old")
        }

        val dataCheckString = buildDataCheckString(params)
        val secretKey = hmacSha256Bytes("WebAppData", botToken.toByteArray(StandardCharsets.UTF_8))
        val expectedHash = hmacSha256Hex(dataCheckString, secretKey)
        log.info("initData hash from client: {}", hash)
        log.info("dataCheckString:\n{}", dataCheckString)
        log.info("expected hash: {}", expectedHash)
        if (!constantTimeEquals(expectedHash, hash)) {
            throw IllegalArgumentException("Invalid initData signature")
        }

        val tgUser = objectMapper.readValue(userJson, TelegramUser::class.java)

        return VerifiedInitData(telegramUser = tgUser, authDate = authDate)
    }

    private fun parseQuery(raw: String): Map<String, String> {
        if (raw.isBlank()) return emptyMap()

        return raw.split("&")
            .asSequence()
            .mapNotNull { part ->
                if (part.isBlank()) return@mapNotNull null
                val idx = part.indexOf("=")
                if (idx <= 0) return@mapNotNull null
                val key = part.substring(0, idx)
                val valueEncoded = part.substring(idx + 1)
                val value = URLDecoder.decode(valueEncoded, StandardCharsets.UTF_8)
                key to value
            }
            .toMap()
    }

    private fun buildDataCheckString(params: Map<String, String>): String {
        return params
            .asSequence()
            .filter { it.key != "hash" }
            .sortedBy { it.key }
            .joinToString("\n") { (k, v) -> "$k=$v" }
    }

    private fun sha256(input: String): ByteArray {
        return MessageDigest.getInstance("SHA-256")
            .digest(input.toByteArray(StandardCharsets.UTF_8))
    }

    private fun hmacSha256Hex(data: String, secretKey: ByteArray): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secretKey, "HmacSHA256"))
        val bytes = mac.doFinal(data.toByteArray(StandardCharsets.UTF_8))
        return bytes.joinToString("") { b -> "%02x".format(b) }
    }


    private fun constantTimeEquals(a: String, b: String): Boolean {
        if (a.length != b.length) return false
        var res = 0
        for (i in a.indices) {
            res = res or (a[i].code xor b[i].code)
        }
        return res == 0
    }

    private fun hmacSha256Bytes(keyString: String, message: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(keyString.toByteArray(StandardCharsets.UTF_8), "HmacSHA256"))
        return mac.doFinal(message)
    }
}