APP_NAME=rtsp_websocket_api
PORT=8000
IMAGE_NAME=rtsp-websocket:latest
K8S_DIR=k8s

# -------------------------
# Docker Compose (local)
# -------------------------
build:
	docker-compose build

up:
	docker-compose up -d

logs:
	docker-compose logs -f

stop:
	docker-compose down

restart:
	docker-compose down && docker-compose up -d

shell:
	docker exec -it $(APP_NAME) bash

clean:
	docker system prune -af --volumes

# -------------------------
# Tailscale
# -------------------------
funnel:
	sudo tailscale funnel $(PORT)

status:
	tailscale status

# -------------------------
# Kubernetes
# -------------------------
k8s-minikube-env:
	@echo "→ Activando entorno Docker de Minikube..."
	eval $$(minikube docker-env)

k8s-build:
	eval $$(minikube docker-env) && docker build -t $(IMAGE_NAME) .

k8s-deploy:
	kubectl apply -f $(K8S_DIR)

k8s-delete:
	kubectl delete -f $(K8S_DIR)

k8s-status:
	kubectl get pods -o wide

k8s-logs:
	kubectl logs -l app=rtsp-websocket --tail=100 -f

k8s-access:
	minikube service rtsp-websocket
