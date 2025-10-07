# Docker Help #

To start the Docker container environment, run the command:
```
docker-compose up -d
```

If changing any of the init config or docker build files, ensure the container is rebuilt.

```
docker-compose up -d --force-recreate --build
```

To start an interactive session with the new container 'clinical-database':
```
docker exec -it clinical-database /bin/bash
```
