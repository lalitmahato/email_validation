setup:
	make build
	make mm
	make m
	make cs
	make down
	make up
	make fixture
	make csu

build:
	sudo docker-compose -f docker-compose.yml up -d --build

up:
	docker-compose -f docker-compose.yml up -d
	#docker-compose -f docker-compose.yml up -d --scale celery_worker=4

down:
	docker-compose -f docker-compose.yml down

down_v:
	docker-compose -f docker-compose.yml down -v

mm:
	docker exec -it email_validation python manage.py makemigrations

m:
	docker exec -it email_validation python manage.py migrate

dd:
	docker exec -t email_validation_db  pg_dump -c -U email_validation -d email_validation > email_validation_dump_data_2024_12_12.sql

dr:
	cat email_validation_dump_data_2024_12_12.sql | sudo docker exec -i precious_db psql -U email_validation

rweb:
	docker restart email_validation

ir:
	docker exec -it email_validation pip install -r requirements.txt

csu:
	docker exec -it email_validation python manage.py createsuperuser

lw:
	docker logs email_validation -f

ln:
	docker logs email_validation_nginx -f

cs:
	docker exec -it email_validation python manage.py collectstatic --noinput

shell:
	docker exec -it email_validation python manage.py shell

pylint:
	DJANGO_SETTINGS_MODULE=core.settings pylint --load-plugins=pylint_django .

docker_loc:
	docker exec -it email_validation python manage.py makemessages -l ne

docker_loc_c:
	docker exec -it email_validation python manage.py compilemessages -l ne

loc:
	python3 manage.py makemessages -l ne

loc_c:
	python3 manage.py compilemessages -l ne

fixture:
	docker exec -it email_validation python manage.py loaddata dkim_default_selector
