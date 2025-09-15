# Email Validator API

---

Swagger URL: https://email-validation.lalitmahato.com.np/api/v1/swagger/

Redoc URL: https://email-validation.lalitmahato.com.np/api/v1/redoc/

Celery Flower URL: http://94.136.184.119:5559/

---

### *User Credential* for admin user and celery flower:
```
Username: admin
Password: P@ssw0rd@##!!
```

---
## Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| Backend          | Django/DjangoRestFramework (Python) |
| Database         | PostgreSQL                          |
| Message Broker   | Redis                               |
| Async Tasks      | Celery                              |
| Task Monitering  | Celery Flower                       |
| Auth             | Django Authentication               |
| Frontend         | Django Templates, HTML, CSS, JS     |
| Containerization | Docker                              |


---

## System Features
1. Multiple Email Validation API   
   - Advantages:
     - Able to handel multiple emails.
   - Disadvantages:
     - Unable to validate live SMTP status: For making it scalable, this API is unable to validate live SMTP status for given email because it takes arount 4-5 seconds.
     - If the email domain is new and the domain record does not exist into our database, then it will take around 4-5 seconds to validate live SMTP status.

2. Live Email Validation API
   - Advantages:
     - This API is able to check live SMTP status for given email.
     - Able to get live DNS records.
   - Disadvantages:
     - Waiting time is 3-5 seconds.

3. Auto DNS Record Updater (Every 30 minutes)
   - The system will automatically update the DNS records for the given email domain which is saved into our database.

4. Manual SMTP Server Configuration With DKIM Selector  
   - Advantages:
     - Able to configure SMTP server manually with DKIM selector.
   - Disadvantages:
     - If the DKIM selector is updated into the DNS record then the system will not be able to get DKIM records.
     - Need to configure DKIM selector manually for every smtp server.

---

# Setup Process
## Setup Instructions

1. **Clone Repository**
```
git clone https://github.com/lalitmahato/email_validation.git
```
```
cd email_validation
```

The setup process for this project is pretty simple because it is dockerized. The only thing required is docker.
The project is using `Makefile` to run the commands, so I recommend to use `Makefile` to run the commands. If your
device don't have `Makefile` installed then you can install it by using following command:
```
pip install makefile
```
The given command will install the `Makefile` on your device. If the `Makefile` does not work then you can enter command 
manually. To setup the project in your device. First create a `.env` file and add the following environment variables:

#### Create `.env` file and add the following environment variables:
```dotenv
SECRET_KEY=secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8004
ALLOWED_ORIGINS=http://localhost:8004
SWAGGER_URL=http://localhost:8004/

# Database Config
DB_ENGINE=django.db.backends.postgresql
DB_NAME=email_validator
DB_USER=email_validator
DB_PASSWORD=db_password
DB_HOST=db
DB_PORT=5432

# SMTP Configuration
EMAIL_STATUS=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=email
EMAIL_HOST_USER_FROM=email_from
EMAIL_HOST_PASSWORD=password

# Celery Flower Configuration
flower_username=username
flower_password=password


# Redis DB Setup
BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
Change the values of the environment variables according to your setup.

*Note: If you make the `DEBUG=False` the system configuration enforces to secure connection(SSL), this setup might not work on local environment.
So make sure to make `DEBUG=True` if you are working on local environment.*

### Project Setup With `Makefile`
To run the project you need to have docker installed on your device. Also it is better to have `Makefile` installed on your device.

If you are using `Makefile` then you don't need to run multiple commands. To run the project using `Makefile` you can use following commands:
```
make setup
```
The above command will build the docker image, run migrations, seed data to the database from fixture file, collect static files and restart the project.

The above process also create `superuser` for that it will ask for user information. Enter the requested details and 
it will create super admin user to login to the system.

### Project Setup Without `Makefile`
If you are not using `Makefile` then you need to run multiple commands.
```
docker-compose -f docker-compose.yml up -d --build
```
The above command will build the docker image. After running the above command you need to run the following commands:
```
docker exec -it email_validation python manage.py makemigrations
```
```
docker exec -it email_validation python manage.py migrate
```
The given commands will run migrations. After running the above commands you need to seed the data to the database from fixture file. To do that run the following command:
```
docker exec -it email_validation python manage.py loaddata dkim_default_selector
```
The above command will seed the data to the database from fixture file. After running the above command you need to collect static files. To do that run the following command:
```
docker exec -it email_validation python manage.py collectstatic --noinput
```
After running the above command you need to restart the project. To do that run the following command:
```
docker-compose -f docker-compose.yml down
```
```
docker-compose -f docker-compose.yml up -d
```
The first command will stop the project and the second command will start the project. This way you can run the project without using `Makefile`.

if you also want to create super user to login to the system then you can use following command:
```
docker exec -it email_validation python manage.py createsuperuser
```