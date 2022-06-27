# docker-test


```bash
$ sudo firewall-cmd --zone=public --add-port=4000/tcp --permanent
$ sudo firewall-cmd --reload

# docker data volume
$ docker volume create --name mongodb_dev
$ docker volume ls

$ docker stop $(docker ps -aq)
$ docker rm $(docker ps -aq)
$ docker system prune -a

$ docker run -d -p 27017:27017 --rm --name mongodb -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=1234 -v mongodb_dev:/data/db mongo
$ docker run -it -p 3000:3000 --rm --name node -v ~/nodetest:/usr/src/nodetest shockz/nodetest:0.2 # tty output
$ docker run -d -p 3000:3000 --rm --name node -v ~/nodetest:/usr/src/nodetest shockz/nodetest:0.2 # background
```