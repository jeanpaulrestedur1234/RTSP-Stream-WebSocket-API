APP_NAME=rtsp_websocket_api
PORT=8000

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

funnel:
	sudo tailscale funnel $(PORT)

status:
	tailscale status

clean:
	docker system prune -af --volumes

shell:
	docker exec -it $(APP_NAME) bash
