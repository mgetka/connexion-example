FROM python:3.7.4-alpine

COPY entrypoint.sh uwsgi.yml VERSION setup.py requirements.txt /
COPY src/conexample /src/conexample
COPY migrations /migrations

RUN apk update && apk add build-base postgresql-libs                                            && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev musl-dev linux-headers && \
    python setup.py install                                                                     && \
    pip install uwsgi                                                                           && \
    apk --purge del .build-deps                                                                 && \
    adduser -DH conexample                                                                      && \
    chown conexample:root entrypoint.sh

USER conexample

ENV UWSGI_BIND=0.0.0.0:5000
ENV UWSGI_PROCESSES=2
ENV UWSGI_PROTOCOL=http

ENTRYPOINT ["./entrypoint.sh"]
CMD ["conexample"]
