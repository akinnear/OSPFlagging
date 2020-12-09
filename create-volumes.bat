:: This file creates volumes that are needed to run the docker images
docker volume create --name=mongo-data-flagging
docker volume create --name=mongo-config
docker volume create --name=mongoclient