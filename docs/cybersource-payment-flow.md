# Integración de Pagos con CyberSource Unified Checkout

## Descripcion General

El sistema utiliza **CyberSource Unified Checkout** para procesar pagos de reservaciones hoteleras. Este enfoque permite que el formulario de tarjeta de credito se renderice directamente en el frontend a traves de un iframe seguro de CyberSource, evitando que los datos sensibles de la tarjeta pasen por nuestro backend.

El flujo se divide en dos fases:

1. **Generacion del Capture Context (Token)** — el backend solicita un JWT a CyberSource que el frontend usa para levantar el formulario de pago.
2. **Confirmacion del pago** — una vez que CyberSource procesa el pago en el frontend, el backend recibe la confirmacion, registra la reservacion en Opera PMS y actualiza la BD.

---

## Diagrama de Flujo

```
┌──────────┐         ┌──────────────┐         ┌─────────────┐         ┌───────────┐
│ Frontend │         │   Backend    │         │ CyberSource │         │ Opera PMS │
└────┬─────┘         └──────┬───────┘         └──────┬──────┘         └─────┬─────┘
     │                      │                        │                      │
     │  1. POST /reservations/                       │                      │
     │  (datos de reserva)  │                        │                      │
     │─────────────────────>│                        │                      │
     │                      │                        │                      │
     │                      │  2. Guardar reserva    │                      │
     │                      │     en BD (isPaid=false)                      │
     │                      │                        │                      │
     │                      │  3. POST /up/v1/capture-contexts              │
     │                      │  (payload firmado con HMAC-SHA256)            │
     │                      │───────────────────────>│                      │
     │                      │                        │                      │
     │                      │  4. JWT Token (capture context)               │
     │                      │<───────────────────────│                      │
     │                      │                        │                      │
     │  5. Response: {Token, ReservationId}           │                      │
     │<─────────────────────│                        │                      │
     │                      │                        │                      │
     │  6. Renderizar Unified Checkout               │                      │
     │     con el JWT Token  │                        │                      │
     │──────────────────────────────────────────────>│                      │
     │                      │                        │                      │
     │  7. Usuario completa │                        │                      │
     │     el formulario    │                        │                      │
     │     de pago          │                        │                      │
     │──────────────────────────────────────────────>│                      │
     │                      │                        │                      │
     │  8. CyberSource procesa el pago               │                      │
     │     y retorna ApprovalCode + PaymentId        │                      │
     │<──────────────────────────────────────────────│                      │
     │                      │                        │                      │
     │  9. POST /payment/confirm-payment             │                      │
     │  {ApprovalCode, PaymentId, ReservationId}     │                      │
     │─────────────────────>│                        │                      │
     │                      │                        │                      │
     │                      │  10. Crear reserva en Opera PMS               │
     │                      │──────────────────────────────────────────────>│
     │                      │                        │                      │
     │                      │  11. reservationId + confirmationNumber       │
     │                      │<──────────────────────────────────────────────│
     │                      │                        │                      │
     │                      │  12. Actualizar reserva en BD                 │
     │                      │      isPaid=true                              │
     │                      │      PaymentTokenReference=ApprovalCode       │
     │                      │      PaymentId=PaymentId                      │
     │                      │                        │                      │
     │  13. Response: {reservationId, confirmationNumber}                   │
     │<─────────────────────│                        │                      │
     │                      │                        │                      │
```

---

## Configuracion de CyberSource

### Variables de Entorno Requeridas

```env
MERCHANT_ID=tu_merchant_id
MERCHANT_KEY_ID=tu_key_id
MERCHANT_SECRET_KEY=tu_secret_key_base64
CYBERSOURCE_BASE_URL=https://apitest.cybersource.com
BASE_FRONTEND_URL=https://tu-dominio-frontend.com
```

| Variable | Descripcion |
|---|---|
| `MERCHANT_ID` | Identificador del comercio en CyberSource. Se obtiene desde el panel de CyberSource Business Center. |
| `MERCHANT_KEY_ID` | ID de la llave usada para firmar las peticiones (HTTP Signature). Se genera en CyberSource Business Center > Key Management. |
| `MERCHANT_SECRET_KEY` | Llave secreta en Base64 para firmar peticiones. Se genera junto con el `MERCHANT_KEY_ID`. |
| `CYBERSOURCE_BASE_URL` | URL base de la API. Usar `https://apitest.cybersource.com` para sandbox o `https://api.cybersource.com` para produccion. |
| `BASE_FRONTEND_URL` | URL del frontend. CyberSource la usa como `targetOrigin` para validar el iframe del Unified Checkout. |

### Obtencion de Credenciales

1. Acceder a [CyberSource Business Center](https://ebc2.cybersource.com/) (sandbox) o [produccion](https://ebc.cybersource.com/)
2. Ir a **Payment Configuration > Key Management**
3. Generar una nueva llave de tipo **REST - Shared Secret**
4. Copiar el `Key ID` y el `Shared Secret` generado

---

## Fase 1: Generacion del Capture Context (Token)

### Endpoint: `POST /reservations/`

Este endpoint crea la reservacion en la base de datos y genera el capture context de CyberSource para iniciar el flujo de pago.

#### Request Body

```json
{
  "checkIn": "2026-04-01",
  "checkOut": "2026-04-05",
  "roomTypeCode": "DELUXE",
  "ratePlanCode": "BAR",
  "adults": 2,
  "children": 1,
  "amountBeforeTax": 450.00,
  "promoCode": "SUMMER2026",
  "specialRequests": "Cama extra para nino",
  "guest": {
    "firstName": "Juan",
    "lastName": "Perez",
    "email": "juan.perez@email.com",
    "phone": "+504 9999-9999"
  }
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `checkIn` | string | Si | Fecha de entrada (formato `YYYY-MM-DD`) |
| `checkOut` | string | Si | Fecha de salida (formato `YYYY-MM-DD`) |
| `roomTypeCode` | string | Si | Codigo del tipo de habitacion (debe coincidir con Opera) |
| `ratePlanCode` | string | Si | Codigo del plan tarifario |
| `adults` | int | Si | Cantidad de adultos |
| `children` | int | Si | Cantidad de ninos |
| `amountBeforeTax` | float | Si | Monto total antes de impuestos (USD) |
| `promoCode` | string | No | Codigo promocional |
| `specialRequests` | string | No | Solicitudes especiales |
| `guest` | object | Si | Datos del huesped |
| `guest.firstName` | string | Si | Nombre del huesped |
| `guest.lastName` | string | Si | Apellido del huesped |
| `guest.email` | string | Si | Correo electronico |
| `guest.phone` | string | Si | Numero de telefono |

#### Response (200 OK)

```json
{
  "Status": true,
  "Token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "ReservationId": "01912345-abcd-7def-8901-123456789abc"
}
```

| Campo | Tipo | Descripcion |
|---|---|---|
| `Status` | bool | Indica si la operacion fue exitosa |
| `Token` | string | JWT (capture context) generado por CyberSource. El frontend lo usa para inicializar Unified Checkout. |
| `ReservationId` | string | UUID v7 de la reservacion creada en la BD |

### Proceso Interno de Generacion del Token

El servicio `CybersourceService.create_sale_request()` realiza lo siguiente:

#### 1. Construccion del Payload

Se arma el payload para la API de Capture Contexts con la configuracion del checkout:

```json
{
  "clientVersion": "0.34",
  "targetOrigins": ["https://tu-dominio-frontend.com"],
  "allowedCardNetworks": ["VISA", "MASTERCARD", "AMEX"],
  "allowedPaymentTypes": ["PANENTRY"],
  "country": "HN",
  "locale": "es_US",
  "captureMandate": {
    "billingType": "NONE",
    "requestEmail": false,
    "requestPhone": false,
    "requestShipping": false,
    "showAcceptedNetworkIcons": true
  },
  "completeMandate": {
    "type": "CAPTURE",
    "decisionManager": true,
    "consumerAuthentication": true
  },
  "data": {
    "orderInformation": {
      "amountDetails": {
        "totalAmount": "450.00",
        "currency": "USD"
      }
    },
    "clientReferenceInformation": {
      "code": "01912345-abcd-7def-8901-123456789abc"
    },
    "consumerAuthenticationInformation": {
      "challengeCode": "04",
      "messageCategory": "01"
    }
  }
}
```

| Campo Clave | Descripcion |
|---|---|
| `targetOrigins` | Dominio del frontend, requerido por CyberSource para validar el iframe |
| `allowedCardNetworks` | Redes de tarjeta aceptadas (Visa, Mastercard, Amex) |
| `allowedPaymentTypes` | `PANENTRY` = ingreso manual de tarjeta |
| `completeMandate.type` | `CAPTURE` = cobro inmediato (no solo autorizacion) |
| `completeMandate.decisionManager` | Activa el motor antifraude de CyberSource |
| `completeMandate.consumerAuthentication` | Activa 3D Secure (autenticacion del titular) |
| `data.clientReferenceInformation.code` | ID de la reservacion para rastreo en CyberSource |
| `consumerAuthenticationInformation.challengeCode` | `04` = No challenge requested, solicitud sin challenge 3DS |
| `consumerAuthenticationInformation.messageCategory` | `01` = Payment Authentication |

#### 2. Firma de la Peticion (HTTP Signature)

CyberSource requiere que cada peticion sea firmada usando **HTTP Signature** con HMAC-SHA256. El proceso es:

1. **Generar fecha RFC1123** para el header `Date`
2. **Calcular Digest SHA-256** del payload serializado (Base64)
3. **Construir el string de firma** con los headers en orden:
   ```
   host: apitest.cybersource.com
   date: Thu, 05 Mar 2026 15:30:00 GMT
   request-target: post /up/v1/capture-contexts
   digest: SHA-256=<digest_base64>
   v-c-merchant-id: tu_merchant_id
   ```
4. **Firmar con HMAC-SHA256** usando el `MERCHANT_SECRET_KEY` (decodificado de Base64)
5. **Construir el header Signature** con el formato:
   ```
   keyid="tu_key_id", algorithm="HmacSHA256", headers="host date request-target digest v-c-merchant-id", signature="<firma_base64>"
   ```

#### 3. Envio a CyberSource

Se hace un `POST` a `{CYBERSOURCE_BASE_URL}/up/v1/capture-contexts` con los headers firmados. CyberSource responde con un **JWT token** (status 201) que el frontend usara para renderizar el formulario.

---

## Fase 2: Confirmacion del Pago

### Endpoint: `POST /payment/confirm-payment`

Una vez que el usuario completa el pago en el Unified Checkout de CyberSource (en el frontend), CyberSource retorna los datos de la transaccion al frontend. El frontend entonces llama a este endpoint para confirmar y finalizar la reservacion.

#### Request Body

```json
{
  "ApprovalCode": "831000",
  "PaymentId": "7123456789012345678901",
  "ReservationId": "01912345-abcd-7def-8901-123456789abc"
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `ApprovalCode` | string | Si | Codigo de aprobacion retornado por CyberSource tras el pago exitoso |
| `PaymentId` | string | Si | Identificador unico de la transaccion de pago en CyberSource |
| `ReservationId` | string | Si | UUID de la reservacion creada en la Fase 1 |

#### Proceso Interno

1. **Obtener la reservacion** de la BD usando el `ReservationId`
2. **Crear la reservacion en Opera PMS** — se envia toda la informacion del huesped, habitacion, tarifa, etc. al sistema hotelero Oracle Opera
3. **Actualizar la reservacion en la BD** con:
   - `isPaid = true`
   - `reservationId` = ID de Opera
   - `confirmationNumber` = Numero de confirmacion de Opera
   - `PaymentTokenReference` = `ApprovalCode` de CyberSource
   - `PaymentId` = ID de transaccion de CyberSource

#### Response (200 OK)

```json
{
  "Status": true,
  "Message": "Payment confirmed successfully",
  "reservationId": "123456",
  "confirmationNumber": "789012"
}
```

| Campo | Tipo | Descripcion |
|---|---|---|
| `Status` | bool | Indica si la confirmacion fue exitosa |
| `Message` | string | Mensaje descriptivo del resultado |
| `reservationId` | string | ID de la reservacion en Opera PMS |
| `confirmationNumber` | string | Numero de confirmacion asignado por Opera PMS |

---

## Modelo de Datos

La tabla `reservations` almacena tanto los datos de la reserva como la informacion del pago:

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | UUID v7 | Identificador unico de la reservacion (PK) |
| `checkIn` | string | Fecha de check-in |
| `checkOut` | string | Fecha de check-out |
| `roomTypeCode` | string | Tipo de habitacion |
| `ratePlanCode` | string | Plan tarifario |
| `adults` | int | Cantidad de adultos |
| `children` | int | Cantidad de ninos |
| `amountBeforeTax` | float | Monto antes de impuestos |
| `promoCode` | string | Codigo promocional |
| `specialRequests` | string | Solicitudes especiales |
| `guest_first_name` | string | Nombre del huesped |
| `guest_last_name` | string | Apellido del huesped |
| `guest_email` | string | Email del huesped |
| `guest_phone` | string | Telefono del huesped |
| `isPaid` | bool | `false` al crear, `true` al confirmar pago |
| `createdAt` | datetime | Fecha de creacion del registro |
| `reservationId` | string | ID de reservacion en Opera (se llena al confirmar pago) |
| `confirmationNumber` | string | Numero de confirmacion de Opera (se llena al confirmar pago) |
| `PaymentTokenReference` | string | Codigo de aprobacion de CyberSource |
| `PaymentId` | string | ID de transaccion de CyberSource |

---

## Integracion en el Frontend

Para usar el token generado por el backend, el frontend debe cargar el SDK de CyberSource Unified Checkout:

```html
<script src="https://testflex.cybersource.com/microform/bundle/v2.0/flex-microform.min.js"></script>
```

Y luego inicializar el checkout con el token:

```javascript
const captureContext = response.Token; // Token del POST /reservations/
const reservationId = response.ReservationId;

const checkout = new Flex(captureContext);

checkout.createField('number', { /* opciones */ });
checkout.createField('securityCode', { /* opciones */ });

// Al completar el pago, CyberSource retorna los datos de la transaccion
// que se envian al backend para confirmar:
fetch('/payment/confirm-payment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ApprovalCode: transactionResult.approvalCode,
    PaymentId: transactionResult.paymentId,
    ReservationId: reservationId
  })
});
```

> **Nota**: La URL del SDK cambia segun el ambiente:
> - Sandbox: `https://testflex.cybersource.com/...`
> - Produccion: `https://flex.cybersource.com/...`

---

## Ambientes

| Ambiente | Base URL API | SDK Frontend |
|---|---|---|
| Sandbox | `https://apitest.cybersource.com` | `https://testflex.cybersource.com/microform/bundle/v2.0/flex-microform.min.js` |
| Produccion | `https://api.cybersource.com` | `https://flex.cybersource.com/microform/bundle/v2.0/flex-microform.min.js` |
