#!/bin/bash
python image_version.py --mode patch --dry-run
docker rm -f server
docker run -itd --name server -p 80:80 -p 443:443 syangnub/nginx-uwsgi-falcon-server:0.0.2
