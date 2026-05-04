FROM osixia/openldap:1.5.0

RUN cat > /container/service/slapd/assets/config/bootstrap/ldif/custom/00-base.ldif <<'EOF'
dn: dc=cyber,dc=lab
objectClass: top
objectClass: dcObject
objectClass: organization
dc: cyber
o: Aseguridad Lab

EOF
