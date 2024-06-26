# Theatre API

API service for theatre management written on DRF

## Installing using GitHub:


```shell
git clone the-link-from-your-forked-repo
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
set POSTGRES_HOST=<your db hostname>
set POSTGRES_PASSWORD=<your db password>
set POSTGRES_USER=<your username>
set POSTGRES_PORT=<your db port>
set POSTGRES_DB=<your db name>
python manage.py migrate
python manage.py runserver
```

## Run with docker

Docker should be installed

```shell
docker-compose build
docker-compose up
```

### Getting access
- create user via /api/user/register/
- get access token via /api/user/token/

### Features
- JWT authentication
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing reservation and tickets
- Creating plays with genres, actors
- Uploading images api/theatre/plays/1/upload-image/
- Creating theatre halls
- Adding performances
- Filtering plays and performances