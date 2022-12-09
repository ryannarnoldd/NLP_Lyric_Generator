#!/usr/bin/env bash
docker build -t facetofacebryce/nlp_lyric_generator_container -f dockerfile .
docker run -it -p 8001:8001\
    -e DJANGO_SUPERUSER_USERNAME=plz\
    -e DJANGO_SUPERUSER_EMAIL=admindddd@example.com\
    -e DJANGO_SUPERUSER_PASSWORD=secretnumber45\
    facetofacebryce/nlp_lyric_generator_container