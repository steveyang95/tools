#nginx-uwsgi-falcon-server
A repo with Docker build contents for a nginx uwsgi falcon server.

This repo is for base purposes.

The image runs supervisord, which will handle the separate processes that runs nginx, uwsgi, and memcached. If you
don't need memcached, please just comment or remove out the configuration in supervisord.conf.

The nginx config is set to allow HTTP traffic and does not have SSL settings on. Please check the SSL Certificates
section for more info to make your server use SSL Protocol.

#Building Container
```bash
docker build . -t syangnub/nginx-uwsgi-falcon-server:{version}
docker run -itd --name server -p 80:80 -p 443:443 syangnub/nginx-uwsgi-falcon-server:0.0.1

```

#Versioning Option
Versions are built through the image_version.py file for ease.

Just run the Python script with a specific mode and make sure to update the VERSION file in this directory.

Example: `python image_version.py --mode patch`

##Running Server Locally
To run the container locally and make its' API available over port 8000,use the following command:

`docker run --rm -d -it -p 443:443 -p 9000:9000  syangnub/nginx-uwsgi-falcon-server:0.0.1`

The nginx server is configured to only allow https traffic. If you want to disable this, please go to the nginx.conf
and remove the configuration for https and allow http traffic.

##Logs
For nginx logs, check out /var/log/nginx inside the container.
Check `docker logs` as well for other logs.

# SSL Certificates
Please include your .crt and .key file into /certs directory as server.crt and server.key files. The Dockerfile will
copy /certs/server.crt and /certs/server.key into the Docker image.

Please go to configs/nginx.conf and uncomment the section for stopping HTTP traffic and using the SSL certificates for
HTTPS traffic.
