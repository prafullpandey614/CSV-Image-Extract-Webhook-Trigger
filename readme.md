# Django Image Processing Project

This project is a Django application that processes images from a CSV file. The system accepts a CSV file containing product names and image URLs, compresses the images asynchronously using Celery, and stores the results. The project also supports triggering webhooks upon completion of image processing.



## [API Docs Postman Link](https://documenter.getpostman.com/view/22703914/2sAXjM2r3t)


## Requirements

- Python 3.8+
- Django 5.1
- Redis (for Celery task queue)
- pipenv or virtualenv (for managing virtual environments)

## Setup

### 1. Clone the Repository and create env and start server with worker

```bash
git clone https://github.com/prafullpandey614/CSV-Image-Extract-Webhook-Trigger.git
cd CSV-Image-Extract-Webhook-Trigger
python -m venv env
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
celery -A project worker --loglevel=info
```

```bash
python manage.py runserver
```

Create a .env File and add this code 
```

DJANGO_SECRET_KEY='django-insecure-2)6-+rffop-%fbie4@-gma4z4z8^%ga(owse4m-74t2_6b5(b@'
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1


SITE_DOMAIN=localhost:8000
SITE_PROTOCOL=http

```
