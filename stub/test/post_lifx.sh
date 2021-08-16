#!/usr/bin/env bash

DGV=kome-lamp-1
curl --header "Content-Type: application/json" \
  -k -O \
  --request POST \
  --data '{"power":"on"}' \
  http://localhost:8090/lifx/${DGV}

cat ${DGV}; echo ""
rm ${DGV} || true
