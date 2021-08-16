#!/usr/bin/env bash

DGV=kome-lamp-0
curl -k -O https://localhost:8803/dgv/${DGV}

cat ${DGV}; echo ""
rm ${DGV}
