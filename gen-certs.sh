#!/usr/bin/env bash
# Génère l'AC, les certificats (broker, capteurs, superviseur) et les distribue
set -euo pipefail
cd "$(dirname "$0")"

PKI=pki    
DAYS=825
SENSORS=(sensor_01 sensor_02)
SUPERVISOR=supervisor
BROKER=broker

mkdir -p "$PKI"

# --- Extensions ---------------------------------------------------------------
cat > "$PKI/server.ext" <<EXT
subjectAltName = DNS:broker, DNS:localhost, IP:127.0.0.1
extendedKeyUsage = serverAuth
EXT
cat > "$PKI/client.ext" <<EXT
extendedKeyUsage = clientAuth
EXT

if [ ! -f "$PKI/ca.key" ]; then
  openssl req -x509 -new -nodes -newkey rsa:2048 \
    -keyout "$PKI/ca.key" -out "$PKI/ca.crt" -days "$DAYS" \
    -subj "/CN=AC-IoT" -addext "basicConstraints=critical,CA:TRUE"
fi

issue() {
  local cn="$1" ext="$2"
  openssl req -new -nodes -newkey rsa:2048 \
    -keyout "$PKI/$cn.key" -out "$PKI/$cn.csr" -subj "/CN=$cn"
  openssl x509 -req -in "$PKI/$cn.csr" -CA "$PKI/ca.crt" -CAkey "$PKI/ca.key" \
    -CAcreateserial -out "$PKI/$cn.crt" -days "$DAYS" -extfile "$PKI/$ext"
}

setgrp() {
  chgrp "$1" "$2" 2>/dev/null || sudo chgrp "$1" "$2" 2>/dev/null \
    || echo "ATTENTION : impossible de faire chgrp $1 $2 (à faire à la main avec sudo)"
}

deploy() {
  local cn="$1" dir="$2" gid="$3"
  mkdir -p "$dir"
  cp "$PKI/ca.crt" "$PKI/$cn.crt" "$PKI/$cn.key" "$dir/"
  chmod 644 "$dir/ca.crt" "$dir/$cn.crt"
  chmod 640 "$dir/$cn.key"
  setgrp "$gid" "$dir/$cn.key"
}

issue "$BROKER" server.ext
deploy "$BROKER" broker/runtime/certs 1883

for s in "${SENSORS[@]}"; do
  issue "$s" client.ext
  deploy "$s" "sensor/runtime/certs/$s" 10001
done

issue "$SUPERVISOR" client.ext
deploy "$SUPERVISOR" supervisor/runtime/certs 10002

if [ -f broker/runtime/acl ]; then
  chmod 640 broker/runtime/acl
  setgrp 1883 broker/runtime/acl
fi

echo "Certificats générés et distribués."
echo "Vérification : openssl verify -CAfile $PKI/ca.crt $PKI/*.crt"
