.PHONY: dep nb mk
dep:
	pip install -r requirements.txt
	curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
nb:
	jupyter notebook --no-browser --port=8881 --allow-root --ip=0.0.0.0 >> /tmp/jp.log 2>&1 &
	sleep 3 && wget localhost:8881 -O /dev/null && jt -t solarizedl -T
mk:
	minikube start --force --driver=docker
