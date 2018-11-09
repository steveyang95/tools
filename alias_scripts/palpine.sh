#!/bin/bash

docker commit test syangnub/palpine:$1
docker tag syangnub/palpine:$1 syangnub/palpine:master
docker tag syangnub/palpine:$1 syangnub/palpine:latest

# docker push syangnub/palpine:$1
# docker push syangnub/palpine:master
# docker push syangnub/palpine:latest

docker rm -f test
docker run --name=test --hostname=nubeva -d --privileged -v /var/run/docker.sock:/var/run/docker.sock -v ~/{add a directory}/:/root/work/ -it syangnub/palpine:$1
