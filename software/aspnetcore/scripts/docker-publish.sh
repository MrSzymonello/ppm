#!/bin/bash
DOCKER_ENV=''
DOCKER_TAG=''
case "$CIRCLE_BRANCH" in
  "master")
    DOCKER_ENV=production
    DOCKER_TAG=latest
    ;;
  "dev")
    DOCKER_ENV=development
    DOCKER_TAG=dev
    ;;    
esac

docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
docker build -f Dockerfile.$DOCKER_ENV -t ppm-api:$DOCKER_TAG .
docker tag ppm-api:$DOCKER_TAG $DOCKER_USERNAME/ppm-api:$DOCKER_TAG
docker push $DOCKER_USERNAME/ppm-api:$DOCKER_TAG