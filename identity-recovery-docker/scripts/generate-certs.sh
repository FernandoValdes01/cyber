#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")/.." && pwd)/certs"
mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
  -keyout "$CERT_DIR/ca.key" \
  -out "$CERT_DIR/ca.crt" \
  -subj "/C=CL/ST=RM/L=Santiago/O=Aseguridad/OU=Clase/CN=Aseguridad-CA"

openssl req -newkey rsa:2048 -nodes \
  -keyout "$CERT_DIR/ldap.key" \
  -out "$CERT_DIR/ldap.csr" \
  -subj "/C=CL/ST=RM/L=Santiago/O=Aseguridad/OU=Clase/CN=ldap.cyber.lab"

cat > "$CERT_DIR/ldap.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=@alt_names
[alt_names]
DNS.1=ldap.cyber.lab
DNS.2=openldap
DNS.3=localhost
IP.1=127.0.0.1
EOF

openssl x509 -req -in "$CERT_DIR/ldap.csr" \
  -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
  -out "$CERT_DIR/ldap.crt" -days 825 -sha256 -extfile "$CERT_DIR/ldap.ext"

chmod 600 "$CERT_DIR"/*.key
echo "Certificados generados en $CERT_DIR"
