FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip postgresql libpq-dev postgresql-client postgresql-client-common
RUN pip3 install uwsgi

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

RUN useradd addressbooks

COPY src /src

COPY ./wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

RUN SECRET_KEY=foo python3 /src/manage.py collectstatic --noinput

USER addressbooks

EXPOSE 80
CMD /wait-for-it.sh addressbooks-postgres:5432 && python3 /src/manage.py migrate && uwsgi --http 0.0.0.0:8080 --chdir /src/ --wsgi-file AddressBooks/wsgi.py --die-on-term --master
