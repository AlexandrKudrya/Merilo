package main.kotlin.com.merilo

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.scheduling.annotation.EnableAsync

@SpringBootApplication
@EnableAsync
class MeriloApplication

fun main(args: Array<String>) {
    runApplication<MeriloApplication>(*args)
}