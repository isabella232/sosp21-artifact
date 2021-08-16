NAME="dspace"

.PHONY: cli dq
dq: 
	cd cmd/dq/; go install .
cli: | dq
	$(done)

.PHONY:k8s runtime
k8s:
	minikube start
runtime:
	$(info TBD syncer etc.)
