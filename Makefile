run:
	docker-compose -f devops/docker/docker-compose.yml up -d --build

stop:
	docker-compose -f devops/docker/docker-compose.yml down

test:
	docker-compose -f devops/docker/docker-compose.yml run --rm web sh -c "pytest -vv && flake8"