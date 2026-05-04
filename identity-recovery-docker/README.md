# Identity Recovery Lab (Docker)

Implementacion de referencia para la actividad de **Aseguramiento de Identidad y Gestion de Secretos** usando 2 contenedores:

1. `openldap` con **LDAPS en 636** y certificado firmado por una **CA propia**.
2. `crud-app` (Flask) para CRUD de usuarios y recuperacion de contrasena.

## Requisitos

- Docker + Docker Compose
- OpenSSL

## 1) Preparar secretos y certificados

```bash
cp .env.example .env
chmod 600 .env
openssl rand -hex 32
```

Pega el resultado de `openssl rand -hex 32` en `TOKEN_SECRET_KEY` dentro de `.env`.

Genera CA y certificado del servidor LDAP:

```bash
chmod +x scripts/generate-certs.sh
./scripts/generate-certs.sh
```

## 2) Levantar servicios

```bash
docker compose up --build
```

Servicios:
- LDAP seguro: `ldaps://localhost:636`
- API CRUD: `http://localhost:8080`

## 3) Pruebas rapidas

Crear usuario:

```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{
    "uid":"juan",
    "cn":"Juan",
    "sn":"Perez",
    "mail":"juan@example.com",
    "password":"Temporal123!"
  }'
```

Consultar usuario:

```bash
curl http://localhost:8080/users/juan
```

Solicitar recuperacion (envia correo real segun `.env`):

```bash
curl -X POST http://localhost:8080/password-recovery/request \
  -H "Content-Type: application/json" \
  -d '{"uid":"juan"}'
```

Confirmar recuperacion:

```bash
curl -X POST http://localhost:8080/password-recovery/confirm \
  -H "Content-Type: application/json" \
  -d '{"token":"<TOKEN>","new_password":"NuevaSegura123!"}'
```

## Controles de seguridad cubiertos

- Cifrado en transito: LDAPS/TLS con CA propia.
- Validacion estricta de certificado LDAP desde la app (`CERT_REQUIRED`).
- Token de recuperacion con HMAC-SHA256, expiracion y enlace a `uid`.
- Password hashing en LDAP con `{SSHA}`.
- Secretos por variables de entorno (`.env`), sin hardcoding.

## Notas

- Si cambias `LDAP_BASE_DN` en `.env`, ajusta tambien `ldap/bootstrap/10-people.ldif`.
- Agrega evidencia (capturas + logs) para el entregable.
