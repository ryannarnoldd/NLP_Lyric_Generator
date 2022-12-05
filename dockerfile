# Dockerfile

FROM python:3.8-buster

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/Client_Lyrics_Interface
RUN mkdir -p /opt/app/Generator_Website
RUN mkdir -p /opt/app/staticfiles
COPY ./Client_Lyrics_Interface /opt/app/Client_Lyrics_Interface/
COPY ./Generator_Website /opt/app/Generator_Website/
COPY ./staticfiles /opt/app/staticfiles/
COPY requirements.txt start-server.sh manage.py /opt/app/

WORKDIR /opt/app
RUN pip install -r requirements.txt
RUN chown -R www-data:www-data /opt/app/

# start server
EXPOSE 8001
RUN python3 manage.py migrate
RUN chown -R www-data:www-data /opt/app/db.sqlite3

STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]