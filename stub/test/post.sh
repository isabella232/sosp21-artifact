#!/usr/bin/env bash

DGV=kome-lamp-0
curl --header "Content-Type: application/json" \
  -k -O \
  --request POST \
  --data '{"power":"on"}' \
  https://localhost:8803/dgv/${DGV}

cat ${DGV}; echo ""
rm ${DGV} || true
