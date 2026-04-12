# MP Booking Backend

API backend para el sistema de reservaciones hoteleras del Hotel Mayan. Gestiona el flujo completo de reservaciones: desde la creación de la reserva, el procesamiento de pagos con CyberSource y el registro en Oracle Opera PMS.

## Stack Tecnológico

- **Python 3.10+**
- **FastAPI** — Framework web async
- **SQLAlchemy** — ORM (con MySQL/PyMySQL)
- **Pydantic** — Validación de datos y settings
- **Alembic** — Migraciones de base de datos
- **CyberSource** — Procesamiento de pagos (Unified Checkout)
- **Oracle Opera Cloud PMS** — Sistema de gestión hotelera

## Arquitectura

```
src/
├── core/           # Configuración y settings
├── db/             # Engine y sesión de SQLAlchemy
├── models/         # Modelos ORM (Reservation)
├── repositories/   # Capa de acceso a datos
├── routes/         # Endpoints de la API
├── schemas/        # Schemas Pydantic (request/response)
└── services/       # Lógica de negocio
    ├── cybersource_service.py   # Integración con CyberSource
    ├── opera_service.py         # Integración con Opera PMS
    ├── payment_service.py       # Confirmación de pagos
    └── reservation_service.py   # Gestión de reservaciones
```

## Flujo de Reservación

1. El cliente envía los datos de reservación (`POST /reservations/`)
2. Se persiste la reservación en la BD y se genera un **capture context** (JWT token) de CyberSource
3. El frontend usa el token para renderizar el formulario de pago de CyberSource Unified Checkout
4. Una vez completado el pago, el frontend envía la confirmación (`POST /payment/confirm-payment`)
5. Se registra la reservación en **Opera PMS** y se actualiza el estado de pago en la BD

## Endpoints

| Método | Ruta                         | Descripción                                      |
|--------|------------------------------|--------------------------------------------------|
| POST   | `/reservations/`             | Crea una reservación y retorna el token de pago   |
| GET    | `/reservations/{id}`         | Consulta una reservación por ID                   |
| POST   | `/payment/confirm-payment`   | Confirma el pago y registra en Opera PMS          |

## Configuración

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Base de datos (MySQL)
DATABASE_HOST=
DATABASE_PORT=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_NAME=

# Oracle Opera PMS
OPERA_APP_KEY=
OPERA_CLIENT_ID=
OPERA_CLIENT_SECRET=
OPERA_ENTERPRISE_ID=
OPERA_GATEWAY_URL=
OPERA_HOTEL_ID=
OPERA_SCOPE=

# CyberSource
MERCHANT_ID=
MERCHANT_KEY_ID=
MERCHANT_SECRET_KEY=
CYBERSOURCE_BASE_URL=

# General
BASE_FRONTEND_URL=
QUEUE_CONNECTION=

# Auth (portal / JWT)
JWT_SECRET_KEY=
# Optional: JWT_ALGORITHM=HS256 JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Loyalty (optional)
# LOYALTY_ENABLED=false POINTS_PER_DOLLAR=10 SILVER_THRESHOLD=1000 GOLD_THRESHOLD=5000 PLATINUM_THRESHOLD=15000
```

Ver también `docs/USER_PORTAL_API.md` para contratos del portal.

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn src.main:app --reload
```

## Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```
