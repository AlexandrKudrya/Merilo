# Руководство разработчика

## Требования

- Docker + Docker Compose
- JDK 21+ (для локальной разработки без Docker)
- Maven 3.9+

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo_url> && cd Merilo

# 2. Создать .env из шаблона и заполнить
cp .env.example .env

# 3. Запустить всё через Docker Compose
docker compose up
```

После запуска:
- Backend API: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html

## Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `SPRING_DATASOURCE_URL` | Строка подключения к PostgreSQL | `jdbc:postgresql://db:5432/merilo` |
| `SPRING_DATASOURCE_USERNAME` | Пользователь БД | `postgres` |
| `SPRING_DATASOURCE_PASSWORD` | Пароль БД | `password` |
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | `1234567890:ABC...` |
| `JWT_SECRET` | Секрет для подписи JWT (минимум 32 символа) | `supersecretkey_32chars_minimum!!` |
| `JWT_EXPIRATION_MINUTES` | Срок жизни JWT | `1440` (24 часа) |
| `ANTHROPIC_API_KEY` | Ключ Anthropic API | `sk-ant-...` |
| `S3_ENDPOINT_URL` | Endpoint S3-совместимого хранилища | `https://s3.amazonaws.com` |
| `S3_ACCESS_KEY` | Access key S3 | `AKIA...` |
| `S3_SECRET_KEY` | Secret key S3 | `wJal...` |
| `S3_BUCKET_NAME` | Имя бакета | `merilo-receipts` |

## Локальная разработка (без Docker)

```bash
cd backend

# Собрать проект
mvn clean package -DskipTests

# Запустить (БД должна быть доступна)
mvn spring-boot:run
```

## Тесты

```bash
cd backend

# Запустить все тесты
mvn test

# Конкретный класс
mvn test -Dtest=AuthServiceTest

# Конкретный метод
mvn test -Dtest=AuthServiceTest#"loginOrRegister returns token for existing user"
```

Тесты находятся в `backend/src/test/kotlin/`. Каждый новый API эндпоинт обязан иметь хотя бы один тест.
Фреймворк: **JUnit 5 + MockK**.

## Сборка Docker-образа

```bash
cd backend
docker build -t merilo-backend .
```

Многоступенчатая сборка: Maven на `eclipse-temurin:21` → runtime на `eclipse-temurin:21-jre`.

## Структура backend

```
backend/
├── src/
│   ├── main/kotlin/com/merilo/
│   │   ├── api/
│   │   │   ├── AuthController.kt       # POST /api/v1/auth/telegram
│   │   │   └── UserController.kt       # GET/PATCH /api/v1/users/me
│   │   ├── config/
│   │   │   ├── JwtService.kt           # Генерация и валидация JWT
│   │   │   ├── JwtAuthFilter.kt        # Фильтр авторизации
│   │   │   └── SecurityConfig.kt       # Spring Security конфиг
│   │   ├── common/exception/
│   │   │   └── ApiExceptionHandler.kt  # Глобальный обработчик ошибок
│   │   ├── dto/
│   │   │   ├── AuthRequest.kt
│   │   │   ├── AuthResponse.kt
│   │   │   ├── UserResponse.kt
│   │   │   └── UpdatePaymentMethodsRequest.kt
│   │   ├── integration/telegram/
│   │   │   ├── TelegramInitDataVerifier.kt  # HMAC-SHA256 верификация
│   │   │   └── TelegramUser.kt
│   │   ├── model/
│   │   │   └── UserEntity.kt           # JPA-сущность пользователя
│   │   ├── repository/
│   │   │   └── UserRepository.kt       # Spring Data JPA репозиторий
│   │   ├── service/
│   │   │   ├── AuthService.kt          # Логика авторизации
│   │   │   └── UserService.kt          # Логика пользователя
│   │   └── MeriloApplication.kt        # Точка входа Spring Boot
│   └── test/kotlin/com/merilo/
│       ├── integration/telegram/
│       │   └── TelegramInitDataVerifierTest.kt
│       └── service/
│           ├── AuthServiceTest.kt
│           └── UserServiceTest.kt
└── pom.xml
```

## Git-конвенции

Conventional commits:

```
feat: add item selection endpoint
fix: handle missing user in participants
chore: update dependencies
docs: add API reference
test: cover order summary endpoint
```

Один PR — одна задача. Описания коммитов на английском.
