# TO-DO.md

# Proyecto: Sistema Seguro de Recuperación de Contraseñas con OpenLDAP

## Objetivo general

Construir una aplicación web CRUD que gestione usuarios en OpenLDAP y permita recuperación segura de contraseñas mediante enlaces temporales firmados con HMAC-SHA256, usando LDAPS en puerto 636, certificados propios, hashing seguro de contraseñas y gestión de secretos mediante variables de entorno.

El proyecto debe mantenerse organizado, bien separado por responsabilidades y fácil de revisar. Cada parte debe estar ubicada donde corresponde: configuración, certificados, lógica de LDAP, lógica de tokens, correo, documentación y evidencias.

---

# 1. Organización general del proyecto

## 1.1. Orden y separación de responsabilidades

- [ ] Mantener el proyecto ordenado por carpetas claras.
- [ ] Separar la configuración del código fuente.
- [ ] Separar la lógica de conexión LDAP de la lógica de la interfaz.
- [ ] Separar la lógica de recuperación de contraseña de la lógica CRUD.
- [ ] Separar la lógica de envío de correo de la lógica de tokens.
- [ ] Separar documentación técnica de evidencias.
- [ ] Evitar archivos gigantes con demasiadas responsabilidades.
- [ ] Usar nombres de archivos claros y descriptivos.
- [ ] Mantener comentarios útiles, no excesivos.
- [ ] Mantener README, TO-DO y documentación actualizados.

## 1.2. Archivos mínimos esperados

- [ ] `README.md`
- [ ] `TO-DO.md`
- [ ] `.gitignore`
- [ ] `.env.example`
- [ ] `docker-compose.yml`
- [ ] Código fuente de la aplicación web.
- [ ] Archivos LDIF para estructura LDAP inicial.
- [ ] Scripts o instrucciones para generar certificados.
- [ ] Documentación de trazabilidad.
- [ ] Documentación de análisis de riesgos.
- [ ] Evidencias de pruebas.

## 1.3. Buenas prácticas de orden

- [ ] No mezclar secretos con código.
- [ ] No mezclar certificados privados con documentación.
- [ ] No dejar archivos temporales innecesarios.
- [ ] No subir credenciales reales.
- [ ] No subir `.env`.
- [ ] No subir llaves privadas.
- [ ] Mantener `.env.example` como plantilla limpia.
- [ ] Mantener evidencias con datos sensibles ocultos.
- [ ] Usar nombres consistentes para variables de entorno.
- [ ] Usar nombres consistentes para servicios y rutas.

---

# 2. Preparación inicial

## 2.1. Repositorio

- [ ] Crear repositorio del proyecto.
- [ ] Crear estructura inicial ordenada.
- [ ] Crear archivo `.gitignore`.
- [ ] Crear archivo `.env.example`.
- [ ] Crear archivo `README.md`.
- [ ] Crear archivo `TO-DO.md`.
- [ ] Crear carpeta o sección para documentación.
- [ ] Crear carpeta o sección para evidencias.
- [ ] Confirmar que el proyecto se puede levantar desde cero siguiendo instrucciones.

## 2.2. `.gitignore`

- [ ] Agregar `.env`.
- [ ] Agregar archivos de llaves privadas.
- [ ] Agregar archivos temporales.
- [ ] Agregar logs.
- [ ] Agregar carpetas de dependencias.
- [ ] Agregar cachés del lenguaje usado.
- [ ] Confirmar que `.env.example` sí queda versionado.

Contenido mínimo sugerido:

```gitignore
.env
.env.*
!.env.example

*.log

certs/*.key
certs/*.srl
certs/*.csr

__pycache__/
node_modules/
dist/
build/
.cache/
```

## 2.3. Variables de entorno

- [ ] Crear `.env.example` sin secretos reales.
- [ ] Crear `.env` real basado en `.env.example`.
- [ ] Proteger `.env` con permisos `600`.
- [ ] Generar secret key de alta entropía.
- [ ] Documentar cada variable necesaria.

Variables mínimas esperadas:

```env
LDAP_URI=ldaps://openldap:636
LDAP_BASE_DN=dc=empresa,dc=local
LDAP_USERS_DN=ou=users,dc=empresa,dc=local
LDAP_BIND_DN=cn=admin,dc=empresa,dc=local
LDAP_ADMIN_PASSWORD=change_me

LDAP_CA_CERT_PATH=/certs/ca.crt

TOKEN_SECRET_KEY=change_me
TOKEN_EXPIRATION_MINUTES=15

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=change_me
SMTP_PASSWORD=change_me
SMTP_FROM=no-reply@example.com
SMTP_USE_STARTTLS=true

APP_BASE_URL=http://localhost:8080
```

Comandos recomendados:

```bash
openssl rand -hex 32
chmod 600 .env
```

---

# 3. OpenLDAP

## 3.1. Levantar OpenLDAP

- [ ] Configurar servicio OpenLDAP en contenedor.
- [ ] Definir dominio LDAP.
- [ ] Definir organización.
- [ ] Definir usuario administrador.
- [ ] Definir contraseña de administrador mediante variable de entorno.
- [ ] Crear volumen persistente para datos LDAP.
- [ ] Crear volumen persistente para configuración LDAP.
- [ ] Levantar contenedor correctamente.
- [ ] Revisar logs del servicio.
- [ ] Confirmar que OpenLDAP queda operativo.

Dominio recomendado:

```text
dc=empresa,dc=local
```

Administrador recomendado:

```text
cn=admin,dc=empresa,dc=local
```

## 3.2. Crear estructura base del directorio

- [ ] Crear unidad organizativa `ou=users`.
- [ ] Crear unidad organizativa `ou=groups`.
- [ ] Crear archivo LDIF para estructura base.
- [ ] Aplicar archivo LDIF.
- [ ] Verificar estructura con `ldapsearch`.

Estructura esperada:

```text
dc=empresa,dc=local
├── ou=users
└── ou=groups
```

Ejemplo de `base.ldif`:

```ldif
dn: ou=users,dc=empresa,dc=local
objectClass: organizationalUnit
ou: users

dn: ou=groups,dc=empresa,dc=local
objectClass: organizationalUnit
ou: groups
```

## 3.3. Usuarios de prueba

- [ ] Crear al menos dos usuarios de prueba.
- [ ] Cada usuario debe tener UID.
- [ ] Cada usuario debe tener nombre.
- [ ] Cada usuario debe tener apellido.
- [ ] Cada usuario debe tener correo.
- [ ] Cada usuario debe tener contraseña con hash SSHA.
- [ ] Verificar usuarios con `ldapsearch`.
- [ ] Confirmar que no hay contraseñas en texto plano.

Atributos mínimos recomendados:

```ldif
objectClass: inetOrgPerson
cn:
sn:
uid:
mail:
userPassword:
```

## 3.4. Hashing de contraseñas

- [ ] Usar mínimo esquema `{SSHA}`.
- [ ] Generar hashes con herramienta compatible con OpenLDAP.
- [ ] Documentar cómo se genera el hash.
- [ ] Confirmar que `userPassword` no se almacena en texto plano.
- [ ] Probar cambio de contraseña.

Comando de referencia:

```bash
docker exec -it openldap slappasswd -h {SSHA}
```

---

# 4. Certificados y LDAPS

## 4.1. Autoridad Certificadora propia

- [ ] Crear llave privada de la CA.
- [ ] Crear certificado público de la CA.
- [ ] Guardar certificado público `ca.crt`.
- [ ] Proteger llave privada `ca.key`.
- [ ] Documentar el uso de la CA.

Archivos esperados:

```text
ca.key
ca.crt
```

## 4.2. Certificado del servidor LDAP

- [ ] Crear llave privada del servidor LDAP.
- [ ] Crear solicitud de firma del certificado.
- [ ] Firmar certificado LDAP con la CA propia.
- [ ] Incluir `subjectAltName`.
- [ ] Incluir `DNS:openldap`.
- [ ] Incluir `DNS:localhost` para pruebas locales.
- [ ] Proteger la llave privada del servidor.

Archivos esperados:

```text
ldap.key
ldap.csr
ldap.crt
```

## 4.3. Configurar LDAPS

- [ ] Configurar OpenLDAP para usar certificado del servidor.
- [ ] Configurar OpenLDAP para usar llave privada del servidor.
- [ ] Configurar OpenLDAP para usar certificado de la CA.
- [ ] Habilitar LDAPS en puerto `636`.
- [ ] Verificar que el puerto `636` responde.
- [ ] Confirmar que la aplicación usará `ldaps://openldap:636`.
- [ ] Evitar que la aplicación use `ldap://` inseguro.

## 4.4. Pruebas de LDAPS

- [ ] Probar certificado con `openssl s_client`.
- [ ] Confirmar `Verify return code: 0 (ok)`.
- [ ] Probar búsqueda LDAP usando LDAPS.
- [ ] Usar la CA propia para validar el servidor.
- [ ] Guardar salida de prueba como evidencia.

Comandos de referencia:

```bash
openssl s_client -connect localhost:636 -CAfile certs/ca.crt
```

```bash
LDAPTLS_CACERT=./certs/ca.crt ldapsearch -x \
  -H ldaps://localhost:636 \
  -D "cn=admin,dc=empresa,dc=local" \
  -W \
  -b "dc=empresa,dc=local"
```

---

# 5. Aplicación web CRUD

## 5.1. Configuración segura de la app

- [ ] Leer configuración desde variables de entorno.
- [ ] No hardcodear credenciales LDAP.
- [ ] No hardcodear credenciales SMTP.
- [ ] No hardcodear secret key de tokens.
- [ ] Cargar certificado CA desde variable de entorno.
- [ ] Conectarse a LDAP usando LDAPS.
- [ ] Validar certificado del servidor LDAP.
- [ ] Manejar errores sin exponer información sensible.
- [ ] Mantener configuración separada de la lógica.

## 5.2. Conexión con OpenLDAP

- [ ] Crear módulo o archivo separado para conexión LDAP.
- [ ] Implementar bind con usuario administrador o usuario de servicio.
- [ ] Implementar búsqueda de usuarios.
- [ ] Implementar creación de usuarios.
- [ ] Implementar modificación de usuarios.
- [ ] Implementar eliminación de usuarios.
- [ ] Implementar cambio de contraseña.
- [ ] Cerrar conexiones correctamente.
- [ ] Manejar errores de conexión.

## 5.3. Crear usuario

- [ ] Crear formulario o endpoint para crear usuario.
- [ ] Validar UID.
- [ ] Validar correo.
- [ ] Validar nombre.
- [ ] Validar apellido.
- [ ] Validar contraseña inicial.
- [ ] Crear DN del usuario.
- [ ] Crear entrada LDAP.
- [ ] Guardar contraseña con hash compatible.
- [ ] Mostrar mensaje de éxito o error controlado.

## 5.4. Listar usuarios

- [ ] Crear vista o endpoint para listar usuarios.
- [ ] Consultar usuarios desde `ou=users`.
- [ ] Mostrar UID.
- [ ] Mostrar nombre.
- [ ] Mostrar apellido.
- [ ] Mostrar correo.
- [ ] No mostrar `userPassword`.
- [ ] Manejar errores de búsqueda.

## 5.5. Editar usuario

- [ ] Crear formulario o endpoint para editar usuario.
- [ ] Permitir editar nombre.
- [ ] Permitir editar apellido.
- [ ] Permitir editar correo.
- [ ] Validar campos antes de modificar.
- [ ] Aplicar cambios con operación LDAP modify.
- [ ] Mostrar mensaje de éxito o error controlado.

## 5.6. Eliminar usuario

- [ ] Crear acción para eliminar usuario.
- [ ] Confirmar eliminación antes de ejecutar.
- [ ] Eliminar entrada LDAP correspondiente.
- [ ] Manejar caso de usuario inexistente.
- [ ] Registrar evento sin información sensible.

## 5.7. Cambio de contraseña administrativo

- [ ] Crear opción para cambiar contraseña de usuario.
- [ ] Validar longitud mínima.
- [ ] Confirmar nueva contraseña.
- [ ] Hashear contraseña.
- [ ] Actualizar atributo `userPassword`.
- [ ] No mostrar contraseña en logs.
- [ ] No mostrar hash innecesariamente.

---

# 6. Recuperación segura de contraseña

## 6.1. Solicitud de recuperación

- [ ] Crear pantalla o endpoint "Olvidé mi contraseña".
- [ ] Solicitar correo o UID.
- [ ] Buscar usuario en OpenLDAP.
- [ ] No revelar si el usuario existe o no.
- [ ] Mostrar mensaje genérico.
- [ ] Generar token solo si el usuario existe.
- [ ] Enviar enlace al correo registrado.

Mensaje recomendado:

```text
Si la cuenta existe, se enviará un enlace de recuperación al correo registrado.
```

## 6.2. Token HMAC-SHA256

- [ ] Crear módulo o archivo separado para tokens.
- [ ] Generar token con UID.
- [ ] Agregar expiración de 15 minutos.
- [ ] Firmar con HMAC-SHA256.
- [ ] Usar secret key desde variable de entorno.
- [ ] Usar secret key de alta entropía.
- [ ] No imprimir token completo en logs.
- [ ] No guardar secret key en código.

Estructura sugerida:

```text
uid:expires:signature
```

Firma sugerida:

```text
HMAC_SHA256(secret, uid + ":" + expires)
```

## 6.3. Validación del token

- [ ] Separar UID, expiración y firma.
- [ ] Verificar formato del token.
- [ ] Verificar expiración.
- [ ] Recalcular firma.
- [ ] Comparar firmas de forma segura.
- [ ] Rechazar token expirado.
- [ ] Rechazar token modificado.
- [ ] Rechazar token malformado.
- [ ] Rechazar token de usuario inexistente.
- [ ] Registrar intento inválido sin exponer token completo.

## 6.4. Restablecimiento de contraseña

- [ ] Crear pantalla o endpoint para nueva contraseña.
- [ ] Validar token antes de permitir cambio.
- [ ] Solicitar nueva contraseña.
- [ ] Solicitar confirmación de contraseña.
- [ ] Validar longitud mínima.
- [ ] Confirmar que ambas contraseñas coincidan.
- [ ] Generar hash SSHA o compatible.
- [ ] Actualizar `userPassword` en OpenLDAP.
- [ ] Mostrar mensaje de éxito.
- [ ] Evitar reutilizar el enlace si implementan control adicional.

## 6.5. Pruebas del token

- [ ] Token válido permite cambiar contraseña.
- [ ] Token expirado es rechazado.
- [ ] Token con UID modificado es rechazado.
- [ ] Token con expiración modificada es rechazado.
- [ ] Token con firma modificada es rechazado.
- [ ] Token malformado es rechazado.
- [ ] Token de usuario inexistente es rechazado.

---

# 7. Correo seguro

## 7.1. Configuración SMTP

- [ ] Usar cuenta de correo real.
- [ ] Configurar SMTP con STARTTLS o SMTPs.
- [ ] Leer host desde variable de entorno.
- [ ] Leer puerto desde variable de entorno.
- [ ] Leer usuario desde variable de entorno.
- [ ] Leer contraseña desde variable de entorno.
- [ ] Leer remitente desde variable de entorno.
- [ ] No hardcodear credenciales SMTP.
- [ ] Mantener lógica de correo separada del resto del código.

## 7.2. Envío de enlace de recuperación

- [ ] Construir enlace con token.
- [ ] Usar `APP_BASE_URL`.
- [ ] Enviar enlace al correo del usuario.
- [ ] Indicar expiración de 15 minutos.
- [ ] No enviar contraseña temporal en texto plano.
- [ ] No incluir información sensible innecesaria.
- [ ] Manejar error de envío.
- [ ] Registrar evento sin exponer el token completo.

Mensaje sugerido:

```text
Se solicitó una recuperación de contraseña para tu cuenta.

Puedes restablecerla usando el siguiente enlace:
{link}

Este enlace estará disponible durante 15 minutos.

Si no solicitaste este cambio, ignora este mensaje.
```

## 7.3. Pruebas de correo

- [ ] Verificar envío real.
- [ ] Verificar uso de STARTTLS o SMTPs.
- [ ] Verificar recepción del enlace.
- [ ] Verificar que el enlace funciona.
- [ ] Verificar que el enlace expira.
- [ ] Guardar evidencia ocultando datos sensibles.

---

# 8. Seguridad de la aplicación

## 8.1. Validación de entradas

- [ ] Validar UID.
- [ ] Validar correo.
- [ ] Validar longitud de campos.
- [ ] Validar caracteres permitidos.
- [ ] Evitar inyección LDAP.
- [ ] Escapar filtros LDAP si corresponde.
- [ ] No construir filtros LDAP de forma insegura.
- [ ] Rechazar datos malformados.
- [ ] Mostrar errores controlados.

## 8.2. Manejo de errores

- [ ] No mostrar stack traces al usuario.
- [ ] No mostrar credenciales.
- [ ] No mostrar tokens completos.
- [ ] No mostrar DN administrativo si no es necesario.
- [ ] No mostrar detalles internos de LDAP.
- [ ] Registrar errores técnicos en logs internos.
- [ ] Mostrar mensajes genéricos al usuario.

## 8.3. Logs seguros

- [ ] Registrar creación de usuario.
- [ ] Registrar modificación de usuario.
- [ ] Registrar eliminación de usuario.
- [ ] Registrar solicitud de recuperación.
- [ ] Registrar token inválido sin token completo.
- [ ] Registrar error de correo sin contraseña SMTP.
- [ ] No registrar contraseñas.
- [ ] No registrar secret key.
- [ ] No registrar credenciales SMTP.
- [ ] No registrar `.env`.

## 8.4. Control de acceso recomendado

- [ ] Definir si el CRUD tendrá login administrativo.
- [ ] Proteger rutas administrativas.
- [ ] Separar rutas públicas de rutas administrativas.
- [ ] Evitar que cualquier usuario pueda eliminar cuentas.
- [ ] Documentar el alcance si el login administrativo no se implementa.
- [ ] Mantener recuperación de contraseña como flujo público controlado.

---

# 9. Gestión de secretos

## 9.1. Secretos obligatorios fuera del código

- [ ] Contraseña del administrador LDAP.
- [ ] Contraseña de configuración LDAP si aplica.
- [ ] Secret key para tokens HMAC.
- [ ] Usuario SMTP.
- [ ] Contraseña SMTP.
- [ ] Llaves privadas de certificados.
- [ ] Cualquier token o credencial real.

## 9.2. Protección de secretos

- [ ] `.env` no debe estar versionado.
- [ ] `.env.example` sí debe estar versionado.
- [ ] `.env.example` no debe contener secretos reales.
- [ ] `.env` debe tener permisos `600`.
- [ ] SecretKey debe generarse con `openssl rand -hex 32`.
- [ ] Llaves privadas deben tener permisos restrictivos.
- [ ] Revisar que no haya secretos en commits.
- [ ] Revisar que no haya secretos en logs.
- [ ] Revisar que no haya secretos en capturas.

Comandos útiles:

```bash
chmod 600 .env
chmod 600 certs/*.key
git status
git diff
```

---

# 10. Pruebas funcionales

## 10.1. Pruebas de infraestructura

- [ ] El proyecto levanta con `docker compose up -d` o equivalente.
- [ ] OpenLDAP inicia correctamente.
- [ ] La app inicia correctamente.
- [ ] La app puede resolver el hostname de OpenLDAP.
- [ ] La app puede conectarse a `ldaps://openldap:636`.
- [ ] Los servicios quedan en la misma red interna.
- [ ] No se exponen puertos innecesarios.

## 10.2. Pruebas LDAPS

- [ ] Puerto `636` responde.
- [ ] Certificado está firmado por CA propia.
- [ ] Validación con CA correcta funciona.
- [ ] Validación sin CA falla o no es aceptada.
- [ ] La app no usa LDAP inseguro.
- [ ] La app valida el certificado del servidor.
- [ ] Guardar evidencia.

## 10.3. Pruebas CRUD

- [ ] Crear usuario desde la app.
- [ ] Listar usuario creado.
- [ ] Editar usuario.
- [ ] Cambiar correo.
- [ ] Cambiar contraseña.
- [ ] Eliminar usuario.
- [ ] Confirmar eliminación con búsqueda LDAP.
- [ ] Confirmar que no se muestra `userPassword`.

## 10.4. Pruebas de recuperación

- [ ] Solicitar recuperación.
- [ ] Recibir correo.
- [ ] Abrir enlace.
- [ ] Cambiar contraseña.
- [ ] Validar que la contraseña cambió en LDAP.
- [ ] Token expirado falla.
- [ ] Token alterado falla.
- [ ] Token malformado falla.
- [ ] No se revela si el usuario existe.

## 10.5. Pruebas de secretos

- [ ] `.env` no aparece en Git.
- [ ] SecretKey no aparece en código.
- [ ] Credenciales SMTP no aparecen en código.
- [ ] Contraseña LDAP no aparece en código.
- [ ] Llaves privadas no aparecen en Git.
- [ ] Permisos de `.env` correctos.
- [ ] Permisos de llaves privadas correctos.

---

# 11. Documentación

## 11.1. README.md

- [ ] Explicar objetivo del proyecto.
- [ ] Explicar cómo levantar el proyecto.
- [ ] Explicar variables de entorno.
- [ ] Explicar cómo generar secret key.
- [ ] Explicar cómo generar certificados.
- [ ] Explicar cómo probar LDAPS.
- [ ] Explicar cómo usar el CRUD.
- [ ] Explicar cómo probar recuperación de contraseña.
- [ ] Explicar buenas prácticas aplicadas.
- [ ] Explicar limitaciones del proyecto.

## 11.2. Matriz de trazabilidad

- [ ] Crear documento de matriz de trazabilidad.
- [ ] Incluir control técnico.
- [ ] Incluir implementación realizada.
- [ ] Incluir función NIST CSF 2.0.
- [ ] Incluir artículo relacionado de Ley 21.459.
- [ ] Mantener redacción clara y defendible.

Tabla base:

```markdown
| Control Técnico | Implementación Realizada | Función NIST 2.0 | Art. Ley 21.459 Relacionado |
|---|---|---|---|
| Cifrado de canal | LDAPS en puerto 636 con certificado firmado por CA propia | Proteger (PR) | Art. 3 Interceptación ilícita |
| Validación del servidor LDAP | App carga ca.crt y valida identidad del servidor | Proteger (PR) | Art. 3 Interceptación ilícita |
| Integridad de URL | Token HMAC-SHA256 con UID y expiración | Proteger (PR) / Identificar (ID) | Art. 2 Acceso ilícito |
| Expiración del token | Token válido por 15 minutos | Proteger (PR) | Art. 2 Acceso ilícito |
| Hashing de contraseñas | userPassword almacenado con SSHA | Proteger (PR) | Art. 2 Acceso ilícito |
| Gestión de secretos | Variables de entorno, .env, permisos 600, .gitignore | Gobernar (GV) / Proteger (PR) | Art. 2 Exceder permisos |
| Correo seguro | SMTP con STARTTLS o SMTPs | Proteger (PR) | Art. 3 Interceptación ilícita |
| Evidencias de pruebas | Pruebas de LDAPS, tokens inválidos y secretos | Detectar (DE) / Responder (RS) | Relacionado con trazabilidad y prevención |
```

## 11.3. Análisis de riesgos

- [ ] Identificar activos.
- [ ] Identificar amenazas.
- [ ] Identificar vulnerabilidades.
- [ ] Identificar riesgos.
- [ ] Identificar impacto.
- [ ] Relacionar controles implementados.
- [ ] Explicar por qué los controles reducen el riesgo.

Activos mínimos:

```text
- Directorio OpenLDAP
- Datos de usuarios
- Contraseñas hasheadas
- SecretKey HMAC
- Credenciales SMTP
- Certificados TLS
- Aplicación web
- Archivo .env
```

Amenazas mínimas:

```text
- Interceptación de credenciales
- Suplantación del servidor LDAP
- Robo de secretos
- Manipulación de enlace de recuperación
- Uso de token expirado
- Enumeración de usuarios
- Exposición de contraseñas
- Acceso no autorizado al CRUD
```

Controles mínimos:

```text
- LDAPS
- CA propia
- Validación estricta de certificado
- HMAC-SHA256
- Expiración de token
- Hash SSHA
- Variables de entorno
- .gitignore
- Permisos 600
- STARTTLS/SMTPs
```

## 11.4. Evidencias

- [ ] Evidencia de servicios levantados.
- [ ] Evidencia de OpenLDAP operativo.
- [ ] Evidencia de LDAPS puerto 636.
- [ ] Evidencia de certificado validado.
- [ ] Evidencia de búsqueda LDAP por LDAPS.
- [ ] Evidencia de usuario creado.
- [ ] Evidencia de contraseña hasheada.
- [ ] Evidencia de correo recibido.
- [ ] Evidencia de token válido.
- [ ] Evidencia de token expirado.
- [ ] Evidencia de token alterado.
- [ ] Evidencia de `.env` protegido.
- [ ] Evidencia de `.env` ignorado por Git.

---

# 12. Funcionalidades esperadas

## 12.1. Funcionalidades obligatorias

- [ ] Aplicación web CRUD.
- [ ] Gestión de usuarios en OpenLDAP.
- [ ] Conexión mediante LDAPS.
- [ ] Uso obligatorio de puerto 636.
- [ ] Validación de certificado de servidor LDAP.
- [ ] CA propia generada con OpenSSL.
- [ ] Certificado LDAP firmado por CA propia.
- [ ] Creación de usuarios.
- [ ] Listado de usuarios.
- [ ] Edición de usuarios.
- [ ] Eliminación de usuarios.
- [ ] Cambio de contraseña.
- [ ] Recuperación de contraseña.
- [ ] Token HMAC-SHA256.
- [ ] Token vinculado al UID.
- [ ] Token con expiración de 15 minutos.
- [ ] Envío de enlace por correo real.
- [ ] Uso de STARTTLS o SMTPs.
- [ ] Contraseñas almacenadas mínimo con SSHA.
- [ ] Secretos mediante variables de entorno.

## 12.2. Funcionalidades de seguridad

- [ ] No usar LDAP inseguro desde la app.
- [ ] No desactivar validación TLS.
- [ ] No aceptar certificados inválidos.
- [ ] No guardar contraseñas en texto plano.
- [ ] No guardar secretos en código.
- [ ] No subir `.env`.
- [ ] No subir llaves privadas.
- [ ] No registrar contraseñas.
- [ ] No registrar tokens completos.
- [ ] Validar entradas.
- [ ] Evitar inyección LDAP.
- [ ] Usar comparación segura para HMAC.
- [ ] No revelar existencia de usuario en recuperación.
- [ ] Manejar errores de forma controlada.

## 12.3. Funcionalidades opcionales recomendadas

- [ ] Login administrativo para el CRUD.
- [ ] Roles básicos.
- [ ] Rate limiting en recuperación.
- [ ] Invalidación de token después de uso.
- [ ] Registro de auditoría.
- [ ] Healthcheck para OpenLDAP.
- [ ] Healthcheck para la app.
- [ ] Scripts automáticos de configuración.
- [ ] Pruebas automatizadas.
- [ ] Uso de Podman rootless.
- [ ] Interfaz simple, clara y ordenada.

---

# 13. Checklist final antes de entregar

## 13.1. Revisión técnica

- [ ] El proyecto levanta correctamente.
- [ ] OpenLDAP funciona.
- [ ] LDAPS funciona en puerto 636.
- [ ] La app se conecta por LDAPS.
- [ ] La app valida la CA.
- [ ] CRUD funciona.
- [ ] Recuperación funciona.
- [ ] Token expira en 15 minutos.
- [ ] Token alterado falla.
- [ ] Contraseñas quedan hasheadas.
- [ ] Correo se envía con STARTTLS o SMTPs.
- [ ] Secretos están fuera del código.
- [ ] `.env` no está versionado.
- [ ] Documentación está completa.

## 13.2. Revisión de seguridad

- [ ] No se usa `ldap://` desde la app.
- [ ] No se desactiva validación TLS.
- [ ] No se aceptan certificados inválidos.
- [ ] No hay contraseñas en texto plano.
- [ ] No hay tokens completos en logs.
- [ ] No hay llaves privadas en Git.
- [ ] No hay credenciales SMTP en Git.
- [ ] No se revela si un usuario existe al pedir recuperación.
- [ ] Se usa comparación segura para HMAC.
- [ ] Se valida expiración del token.

## 13.3. Revisión documental

- [ ] README completo.
- [ ] TO-DO completo.
- [ ] Matriz de trazabilidad completa.
- [ ] Análisis de riesgos completo.
- [ ] Evidencias completas.
- [ ] Capturas o salidas de comandos incluidas.
- [ ] Datos sensibles ocultos en evidencias.
- [ ] Security by Design explicado.
- [ ] Buenas prácticas explicadas.

---

# 14. Criterio de término

El proyecto se considera terminado cuando:

```text
1. OpenLDAP se ejecuta correctamente.
2. LDAPS funciona en puerto 636.
3. La aplicación se conecta a OpenLDAP validando la CA.
4. La aplicación permite crear, listar, editar y eliminar usuarios.
5. La aplicación permite solicitar recuperación de contraseña.
6. La aplicación genera token HMAC-SHA256 con UID y expiración.
7. El token expira en 15 minutos.
8. El enlace se envía por correo usando STARTTLS o SMTPs.
9. La contraseña nueva queda almacenada en LDAP con hash SSHA.
10. Los secretos están fuera del código.
11. El proyecto está organizado y bien separado por responsabilidades.
12. El reporte contiene matriz de trazabilidad, análisis de riesgos y evidencias.
```
