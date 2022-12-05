#!/usr/bin/env bash
docker build -t nlp_lyric_generator_container .
docker run -it -p 8001:8001\
    -e DJANGO_SUPERUSER_USERNAME=plz\
    -e DJANGO_SUPERUSER_EMAIL=admindddd@example.com\
    -e DJANGO_SUPERUSER_PASSWORD=secretnumber45\
    facetofacebryce/nlp_lyric_generator_container