### Installation and running

**Note:**
The first time you will be running the `exchange-rate-service`, it will fail to start
because the database doesn't exist yet.

Even if there's a script to create the database, it would need to be created manually,
because the container has to be up to run that script, but the container crashes since it fails to run the migration...

To manually create the DB:
- Go to exchange-rate-service `cd exchange-rate-backend`
- Build containers `docker-compose build`
- Run postgres `docker-compose up postgres`
- Run psql inside of docker container `docker exec -it exchange-rate-backend_postgres_1 psql -U postgres`
- Create DB: `CREATE DATABASE exchange_rate_dev;`

Set up
1. Run frontend
- Create a `.env` file and copy the contents from `.env.example` over:
    1. In the service directory:
        `cp .env.example .env`
- Go to exchange-rate-frontend `cd exchange-rate-frontend`
- Run app `npm start`
- Run test `npm test`

2. Run backend
- Create a `.env` file and copy the contents from `.env.example` over:
    1. In the service directory:
        `cp .env.example .env`
    2. to run server
        APP_ENV=local
        APP_COMPONENT=server
    3. to run tests
        APP_ENV=test
        APP_COMPONENT=tests
- Go to exchange-rate-backend `cd exchange-rate-backend`
- Build containers `docker-compose build`
- Run postgres `docker-compose up postgres`
- Run kafka `docker-compose up kafka`
- Run redis `docker-compose up redis`
- Once postgres, kafka, redis is ready `docker-compose up exchange-rate-backend-service`
- run  poller worker `docker-compose up exchangerate-poller`
- run  processor worker `docker-compose up exchangerate-processor`


### Documentaion
1. Backend service Swagger Doc
    1. once service is up and running you can check api http://localhost:5000/docs
2. Backend service Postman
    1. Install/open Postman and import the file in this repo's `postman` directory
