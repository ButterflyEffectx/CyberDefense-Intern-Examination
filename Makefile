.PHONY: up seed post


up:
docker compose up -d --build


seed:
python3 samples/post_logs.py


post:
python3 samples/post_logs.py