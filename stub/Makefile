SHELL := /bin/bash
THIS_VER := v0.0.1

.PHONY: redis, run
redis:
	redis-cli ping || redis-server /usr/local/etc/redis.conf --daemonize yes

run: | redis
	@trap 'kill %1; kill %2' SIGINT; \
	cd js/dgvserver; ts-node server.ts & \
	cd ../../py/v2s; python server.py
