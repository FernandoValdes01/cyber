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

Si vas a probar el dominio inventado desde el host, agrega en `/etc/hosts`:

```bash
127.0.0.1 ldap.cyber.lab
```

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
- LDAP seguro: `ldaps://ldap.cyber.lab:636`
- API CRUD: `http://localhost:8080`
- MailHog: `http://localhost:8025`

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

Login de prueba:

```bash
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"uid":"juan","password":"Temporal123!"}'
```

Solicitar recuperacion (envia correo real segun `.env`):

```bash
curl -X POST http://localhost:8080/password-recovery/request \
  -H "Content-Type: application/json" \
  -d '{"uid":"juan"}'
```

Si usas la configuracion de laboratorio con MailHog, revisa el mensaje en `http://localhost:8025`.

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

- El dominio y DN del laboratorio usan `cyber.lab` / `dc=cyber,dc=lab`.
- Agrega evidencia (capturas + logs) para el entregable.
