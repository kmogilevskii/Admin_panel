# Launching instructions
Create an image and start the server:
```
~/Admin_panel$ sudo docker-compose up --build -d
```

Building and running ETL is done using the etl.sh file

# Technical task

As a second task, we propose to expand the Admin Panel project: launch the application via WSGI/ASGI, set up the delivery of static files via Nginx, and prepare the infrastructure for working with Docker. To do this, push the code that you wrote in the first sprint to the repository and run the tasks from the `tasks` folder.

## Technologies used

- The application runs under the control of a WSGI/ASGI server.
- To serve [static files](https://nginx.org/ru/docs/beginners_guide.html#static) use **Nginx**.
- Virtualization is done in **Docker**.

## Main components of the system

1. **WSGI/ASGI server** - server running the application.
2. **Nginx** - proxy server, which is the entry point for the web application.
3. **PostgreSQL** is a relational data store.
4. **ETL** is a mechanism for updating data between PostgreSQL and ES.

## Service schema

![all](images/all.png)

## Project requirements

1. The application must be launched via WSGI/ASGI.
2. All system components are in Docker.
3. The return of static files is carried out at the expense of Nginx.

## Recommendations for the project

1. The database uses a special user to work with the WSGI/ASGI server.
2. Use docker compose to communicate between containers.
