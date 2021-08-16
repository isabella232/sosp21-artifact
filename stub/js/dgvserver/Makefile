SHELL := /bin/bash
THIS_VER := v0.0.1

redis:
	redis-cli ping || redis-server /usr/local/etc/redis.conf --daemonize yes
run: # | redis
	ts-node server.ts
