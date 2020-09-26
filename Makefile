docker-build:
	docker build -t score-tool:dev .

docker-run:
	docker run -p 8050:8050 -t score-tool:dev