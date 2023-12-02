docker-compose exec backend alembic revision --autogenerate -m "create_table"
docker-compose exec backend alembic upgrade head
# psql -h 127.0.0.1 -U postgres -d fox_db;