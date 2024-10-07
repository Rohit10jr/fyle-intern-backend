# Fyle Backend Challenge

## Who is this for?

This challenge is meant for candidates who wish to intern at Fyle and work with our engineering team. You should be able to commit to at least 6 months of dedicated time for internship.


## Challenge outline

This challenge involves writing a backend service for a classroom. The challenge is described in detail [here](./Application.md)


## Installation

1. Fork this repository to your github account
2. Clone the forked repository and proceed with steps mentioned below

### Install requirements

```
virtualenv env --python=python3.8
source env/bin/activate
pip install -r requirements.txt
```
### Reset DB

```
export FLASK_APP=core/server.py
rm core/store.sqlite3
flask db upgrade -d core/migrations/
```
### Start Server
For Linux/MacOS:
```
bash run.sh
```

For Windows PowerShell:
```
waitress-serve --listen=127.0.0.1:5000 core.server:app
```

### Run Tests
```
pytest -vvv -s tests/

# for test coverage report
# pytest --cov
# open htmlcov/index.html
```

### Dockerization

```
docker build -t fyle-backend-challenge .
```
To start the services using Docker Compose:

```
docker-compose up
```

To stop the services:
```
docker-compose down
```
