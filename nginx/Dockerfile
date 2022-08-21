FROM nginx


WORKDIR /etc/nginx/conf.d

RUN rm default.conf

COPY my_vocab.conf .
COPY "./certs/api.myvocab.io+3.pem" .
COPY "./certs/api.myvocab.io+3-key.pem" .