# Модели данных

## Таблицы базы данных

### users

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | Внутренний ID |
| `telegram_id` | `bigint UNIQUE` | ID пользователя в Telegram |
| `username` | `text NULL` | Telegram username (без @) |
| `payment_methods` | `jsonb` | Способы оплаты (см. ниже) |
| `created_at` | `timestamptz` | Дата регистрации |

**Структура `payment_methods`:**
```json
{
  "tinkoff": "@ivan",
  "sbp": "+7 999 000-00-00",
  "sber": "4276 1234 5678 9012"
}
```
Ключи произвольные — пользователь сам задаёт названия способов оплаты.

---

### orders

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | ID заказа |
| `creator_id` | `bigint FK → users.id` | Создатель заказа |
| `status` | `text` | Статус (см. ниже) |
| `order_info` | `jsonb` | Позиции чека (см. ниже) |
| `photo_url` | `text NULL` | URL фото чека в S3 |
| `created_at` | `timestamptz` | Дата создания |
| `updated_at` | `timestamptz` | Дата последнего изменения |

**Возможные значения `status`:**

| Значение | Описание |
|---|---|
| `DRAFT` | Создан, фото не загружено |
| `PENDING` | Фото загружено, чек распознан, участники выбирают позиции |
| `ACTIVE` | Все выбрали позиции, ждём оплат |
| `FINISHED` | Все оплатили |
| `FAILED` | Ошибка при распознавании чека |

**Структура `order_info`:**
```json
[
  {
    "id": 1,
    "name": "Маргарита 30см",
    "price": 89000,
    "quantity": 2.0,
    "splits": [
      {"user_id": 2, "quantity": 1.0},
      {"user_id": 3, "quantity": 1.0}
    ]
  },
  {
    "id": 2,
    "name": "Кола 0.5л",
    "price": 15000,
    "quantity": 1.0,
    "splits": [
      {"user_id": 2, "quantity": 0.5},
      {"user_id": 3, "quantity": 0.5}
    ]
  }
]
```

> **Важно:** `price` хранится в **копейках** (целое число). 89000 = 890 рублей.

Поле `splits` заполняется когда участники выбирают позиции:
- `user_id` — внутренний ID пользователя (не telegram_id)
- `quantity` — сколько единиц этой позиции взял участник (может быть дробным, например `0.5` для половины блюда)

---

### user_orders

Связь участников с заказами (many-to-many).

| Колонка | Тип | Описание |
|---|---|---|
| `id` | `bigint PK` | ID записи |
| `user_id` | `bigint FK → users.id` | Участник |
| `order_id` | `bigint FK → orders.id` | Заказ |
| `status` | `text` | Статус участника (см. ниже) |
| `created_at` | `timestamptz` | Дата добавления в заказ |

**Возможные значения `status`:**

| Значение | Описание |
|---|---|
| `pending` | Не выбрал позиции / не оплатил |
| `confirmed` | Выбрал позиции, сумма подтверждена |
| `paid` | Оплатил |

---

## Pydantic-схемы

### OrderResponse

Возвращается во всех эндпоинтах работы с заказами.

```python
class OrderResponse(BaseModel):
    id: int
    status: str
    creator_id: int
    order_info: list[OrderItem]   # позиции чека
    participants: list[ParticipantInfo]
    created_at: str
```

### OrderItem

Одна позиция в чеке.

```python
class OrderItem(BaseModel):
    id: int
    name: str
    price: float        # в копейках
    quantity: float
    splits: list[Split] # кто что выбрал
```

### Split

```python
class Split(BaseModel):
    user_id: int    # внутренний ID, не telegram_id
    quantity: float
```

### OrderSummaryResponse

Итоговый расчёт для эндпоинта `GET /orders/{id}/summary`.

```python
class OrderSummaryResponse(BaseModel):
    order_id: int
    participants: list[ParticipantSummary]
    payment_methods: dict  # реквизиты создателя заказа
```

```python
class ParticipantSummary(BaseModel):
    user_id: int
    username: str | None
    amount_due: float  # сколько должен (в рублях)
    status: str        # pending | confirmed | paid
```
