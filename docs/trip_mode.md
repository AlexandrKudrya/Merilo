# Режим поездки — аналитика и проектирование

## Концепция

Режим поездки позволяет группе людей делить расходы на протяжении нескольких мест/заказов. Один заплатил в ресторане, второй в магазине — в конце система считает кто кому сколько должен и минимизирует количество переводов.

---

## Новые сущности БД

### Trip

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | ID поездки |
| `creator_id` | `bigint FK → users.id` | Создатель поездки |
| `name` | `text` | Название поездки |
| `status` | `text` | `ACTIVE` / `CLOSED` |
| `balance_cache` | `jsonb NULL` | Кэш рассчитанных балансов |
| `created_at` | `timestamptz` | Дата создания |

### trip_user

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | ID записи |
| `trip_id` | `bigint FK → trips.id` | Поездка |
| `user_id` | `bigint FK → users.id` | Участник |
| `created_at` | `timestamptz` | Дата добавления |

### trip_order

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | ID записи |
| `trip_id` | `bigint FK → trips.id` | Поездка |
| `order_id` | `bigint FK → orders.id` | Заказ |
| `created_at` | `timestamptz` | Дата привязки |

---

## Триггеры пересчёта баланса

Баланс пересчитывается и сохраняется в `balance_cache` при двух событиях:

1. Заказ из поездки перешёл в статус `ACTIVE` (все участники выбрали позиции)
2. Участник отметил оплату по заказу из поездки

В остальное время отдаётся закэшированное значение.

> При 10–15 заказах на поездку JSONB-запросы не создают проблем с производительностью.

---

## Алгоритм минимизации переводов

Используется **balance подход** (он же greedy debt simplification).

### Шаги:

1. Для каждого участника считаем **чистый баланс**:
   ```
   баланс = сколько заплатил − сколько должен был заплатить
   ```
   - `сколько заплатил` — сумма заказов где он `creator`
   - `сколько должен был` — сумма его splits по всем заказам поездки

2. Получаем два списка: **кредиторы** (баланс > 0) и **должники** (баланс < 0)

3. Жадно схлопываем: берём наибольший минус и наибольший плюс, создаём перевод, уменьшаем балансы. Повторяем пока не обнулятся.

### Пример:

```
А заплатил 300, должен был 100 → баланс +200
Б заплатил 0,   должен был 100 → баланс -100
В заплатил 0,   должен был 100 → баланс -100

Результат:
  Б → А: 100
  В → А: 100
```

Алгоритм гарантирует минимальное количество переводов.

---

## SQL-запросы для расчёта балансов

**Сколько заплатил пользователь** (как creator заказа):

```sql
SELECT
    o.creator_id AS user_id,
    SUM((item->>'price')::bigint * (item->>'quantity')::float) AS paid
FROM orders o
JOIN trip_order t ON o.id = t.order_id
CROSS JOIN jsonb_array_elements(o.order_info) AS item
WHERE t.trip_id = :trip_id
  AND o.status = 'ACTIVE'
GROUP BY o.creator_id
```

**Сколько должен был заплатить** (через splits):

```sql
SELECT
    (split->>'user_id')::bigint AS user_id,
    SUM((item->>'price')::bigint * (split->>'quantity')::float) AS owed
FROM orders o
JOIN trip_order t ON o.id = t.order_id
CROSS JOIN jsonb_array_elements(o.order_info) AS item
CROSS JOIN jsonb_array_elements(item->'splits') AS split
WHERE t.trip_id = :trip_id
  AND o.status = 'ACTIVE'
GROUP BY split->>'user_id'
```

---

## Новые эндпоинты

### POST /trips
Создать поездку.

**Request:**
```json
{ "name": "Питер 2026" }
```
**Response 201:**
```json
{ "id": 1, "name": "Питер 2026", "status": "ACTIVE", "created_at": "..." }
```

---

### POST /trips/{id}/users
Добавить участников в поездку. Только создатель.

**Request:**
```json
{ "telegram_ids": [123456, 789012] }
```
**Response 200:**
```json
{ "added": 2, "participants": [...] }
```

---

### DELETE /trips/{id}/users/{user_id}
Удалить участника из поездки. Только создатель.

**Response 200:**
```json
{ "removed": true }
```

---

### POST /orders
Без изменений, но добавляется опциональное поле `trip_id`.

**Request:**
```json
{ "trip_id": 1 }
```
Если `trip_id` передан — заказ сразу привязывается к поездке через `trip_order`.

---

### POST /trips/{id}/orders
Привязать существующий заказ к поездке постфактум. Только создатель поездки.

**Request:**
```json
{ "order_id": 42 }
```
**Response 200:**
```json
{ "linked": true }
```

---

### GET /trips/{id}
Информация о поездке.

**Response 200:**
```json
{
  "id": 1,
  "name": "Питер 2026",
  "status": "ACTIVE",
  "creator_id": 1,
  "participants": [
    { "user_id": 1, "username": "cenaladta" }
  ],
  "orders": [
    { "order_id": 42, "status": "ACTIVE", "total": 1850 }
  ],
  "created_at": "..."
}
```

---

### GET /trips/{id}/balance
Итоговый расчёт балансов поездки. Отдаётся из кэша если актуален.

**Response 200:**
```json
{
  "trip_id": 1,
  "transfers": [
    {
      "from_user_id": 2,
      "from_username": "vasya",
      "to_user_id": 1,
      "to_username": "cenaladta",
      "amount": 1500,
      "payment_methods": { "sbp": "+79001234567" }
    }
  ]
}
```

---

### GET /trips/{id}/can-close
Проверить можно ли закрыть поездку. Поездка закрывается только если все заказы в статусе `FINISHED`.

**Response 200:**
```json
{
  "can_close": false,
  "reason": "Есть незавершённые заказы",
  "pending_orders": [42, 43]
}
```

---

### PATCH /trips/{id}/close
Закрыть поездку. Только если `can_close = true`.

**Response 200:**
```json
{ "status": "CLOSED" }
```

---

*Trip Mode · аналитика v0.1 · 2026*
