package com.merilo.config

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.authority.SimpleGrantedAuthority
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter



@Component
class JwtAuthFilter(
    private val jwtService: JwtService
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        val header = request.getHeader("Authorization")
        val token = header?.takeIf { it.startsWith("Bearer ") }?.removePrefix("Bearer ")?.trim()

        if (token != null && SecurityContextHolder.getContext().authentication == null) {
            try {
                val userId = jwtService.parseUserId(token)

                val auth = UsernamePasswordAuthenticationToken(
                    userId.toString(),
                    null,
                    listOf(SimpleGrantedAuthority("ROLE_USER"))
                )
                SecurityContextHolder.getContext().authentication = auth
            } catch (_: Exception) {

            }
        }

        filterChain.doFilter(request, response)
    }
}