# Email Validator API 

## Setup Process
### Create ```.env``` file and add the following environment variables:
```dotenv
SECRET_KEY=secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5010
ALLOWED_ORIGINS=http://localhost:5010
SWAGGER_URL=http://localhost:5010/

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

# Pagination Setting
PAGE_SIZE=20

# Redis DB Setup
BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
Change the values of the environment variables according to your setup.

### To run the project:
1. **Build the Docker containers**:
    If you are using ```Makefile``` then run the following command:
    ```bash
    make build
    ```
   **OR** build by using following command:
    ```bash
    docker-compose -f docker-compose.yml up -d --build
    ```
2. **Once the project is successfully build you can use following commands to run the project**:
   - **To run the**:
     If you are using ```Makefile``` then run the following command:
     ```bash
     make up
     ```
     **OR**
     ```bash
     docker-compose -f docker-compose.yml up -d
     ```
   - **To Stop The Project**:
     If you are using ```Makefile``` then run the following command:
     ```bash
     make down
     ```
     **OR**
     ```bash
     docker-compose -f docker-compose.yml down
     ```
   - **To Run Migration**:
     If you are using ```Makefile``` then run the following command:
     ```bash
     make mm
     ```
     ```bash
     make m
     ```
     **OR**
     ```bash
     docker-compose -f docker-compose.yml python manage.py makemigrations
     ```
     ```bash
     docker-compose -f docker-compose.yml python manage.py migrate
     ```
