setup:
	make build
	make mm
	make m
	make cs
	make down
	make up

build:
	sudo docker-compose -f docker-compose.yml up -d --build

up:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose -f docker-compose.yml down

down_v:
	docker-compose -f docker-compose.yml down -v

mm:
	docker exec -it forest_project python manage.py makemigrations

m:
	docker exec -it forest_project python manage.py migrate

dd:
	docker exec -t forest_project_db  pg_dump -c -U forest_project -d forest_project > forest_project_dump_data_2024_12_12.sql

dr:
	cat forest_project_dump_data_2024_12_12.sql | sudo docker exec -i precious_db psql -U forest_project

rweb:
	docker restart forest_project

ir:
	docker exec -it forest_project pip install -r requirements.txt

csu:
	docker exec -it forest_project python manage.py createsuperuser

lw:
	docker logs forest_project -f

ln:
	docker logs forest_project_nginx -f

cs:
	docker exec -it forest_project python manage.py collectstatic --noinput

shell:
	docker exec -it forest_project python manage.py shell

pylint:
	DJANGO_SETTINGS_MODULE=core.settings pylint --load-plugins=pylint_django .

docker_loc:
	docker exec -it forest_project python manage.py makemessages -l ne

docker_loc_c:
	docker exec -it forest_project python manage.py compilemessages -l ne

loc:
	python3 manage.py makemessages -l ne

loc_c:
	python3 manage.py compilemessages -l ne
