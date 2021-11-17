1. Run `docker-compose up --build -d` to build and start the containers
2. Check if the Job Manager is available at `localhost:8088`
3. Submit job with `docker-compose exec jobmanager ./bin/flink run -py code/kafka_to_csv.py`
