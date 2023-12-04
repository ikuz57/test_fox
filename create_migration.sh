#!/bin/bash

docker-compose exec backend alembic revision --autogenerate -m "create_table"
docker-compose exec backend alembic upgrade head
docker-compose exec postgres psql -h 127.0.0.1 -U postgres -d fox_db -c \
"INSERT INTO status (id, name) VALUES (1, 'Открыт');
INSERT INTO status (id, name) VALUES (2, 'В работе');
INSERT INTO status (id, name) VALUES (3, 'Закрыт');"
