# API del portal de usuario (MP Booking)

Convención: **JSON en `snake_case`**. Rutas **sin** prefijo `/api/v1` (mismo estilo que `/reservations` y `/payment`). El OpenAPI en `/docs` refleja los mismos paths.

## Autenticación

Enviar `Authorization: Bearer <access_token>` en rutas protegidas.

**Política de contraseña (registro):** longitud mínima **8**, máxima **72** (límite de bcrypt). Letras, números y símbolos recomendados; validación adicional puede hacerse en el cliente.

---

## `POST /auth/register`

**Body**

```json
{
  "email": "ana@example.com",
  "password": "secretsecret",
  "first_name": "Ana",
  "last_name": "López",
  "country": "HN",
  "phone": "9999-1234",
  "national_id": "0801-1990-12345"
}
```

- **`country`:** obligatorio. Valores admitidos en esta versión: **`"HN"`** | **`"US"`** (el front puede mostrar primero Honduras y Estados Unidos en el selector).
- **`national_id`:** número de identidad / documento (mínimo 3 caracteres).
- **`phone`:** según país se valida y se guarda en **E.164**:
  - **HN:** 8 dígitos (móvil) o 11 dígitos empezando por `504`.
  - **US:** 10 dígitos NANP (si el usuario escribe 11 y empieza por `1`, se interpreta como código de país).

**201** — `AuthResponse`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "0194…",
    "email": "ana@example.com",
    "first_name": "Ana",
    "last_name": "López",
    "country": "HN",
    "phone": "+50499991234",
    "national_id": "0801-1990-12345",
    "points_balance": 0,
    "membership_tier": "bronze",
    "reservation_count": 0,
    "account_verified": false
  }
}
```

**409** — `{"detail": "Email already registered"}`

**422** — errores de validación por campo (`email`, `phone`, `country`, `national_id`, `password`, etc.)

Rate limit: **10/min** por IP.

---

## `POST /auth/login`

**Body**

```json
{
  "email": "ana@example.com",
  "password": "secretsecret"
}
```

**Respuesta:** mismo shape que register (`AuthResponse`).

**401** — `{"detail": "Invalid email or password"}`

Rate limit: **20/min** por IP.

---

## `GET /auth/me`

Requiere `Authorization: Bearer …`

**200** — objeto `PortalUser` (igual que `user` en login).

**401** — token ausente, inválido o usuario borrado.

---

## `PATCH /users/me`

Requiere `Authorization: Bearer …`

**Body** (todos opcionales; solo se actualizan campos enviados)

```json
{
  "first_name": "Ana",
  "last_name": "López",
  "country": "US",
  "phone": "5551234567",
  "national_id": "0801-1990-12345"
}
```

Si envías **`country`**, debes enviar también **`phone`** en el mismo request (el número se valida con las reglas del país elegido).

**200** — `PortalUser` actualizado.

**401** — no autenticado.

**422** — validación de campos o falta de `phone` al cambiar `country`.

El **email** no se modifica por este endpoint (solo lectura en portal; cambio de email = flujo aparte con verificación).

---

## `POST /auth/logout`

**204** — sin cuerpo. Con JWT stateless el cliente elimina el token; este endpoint es no-op para compatibilidad con flujos que esperan cerrar sesión en servidor.

---

## Reservas y usuario

- `POST /reservations` con header `Authorization: Bearer …` asocia la reserva al `user_id` del token.
- Tras pago confirmado (`POST /payment/confirm-payment`), si la reserva tenía `user_id`, se incrementa `reservation_count`. Si `LOYALTY_ENABLED=true`, se suman puntos según `POINTS_PER_DOLLAR` y se recalcula `membership_tier`.

---

## Variables de entorno (auth)

| Variable | Descripción |
|----------|-------------|
| `JWT_SECRET_KEY` | Secreto HS256 (obligatorio en producción) |
| `JWT_ALGORITHM` | Por defecto `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Por defecto `60` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Reservado para futuro refresh token |

---

## OpenAPI

Documentación interactiva: **`/docs`** (Swagger UI) y **`/redoc`**.
