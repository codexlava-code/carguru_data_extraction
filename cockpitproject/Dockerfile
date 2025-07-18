FROM python:3.10


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /srv

COPY Pipfile Pipfile.lock /srv/
RUN pip install pipenv

RUN pipenv install

COPY . .

EXPOSE 5521
CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:5521", "wsgi:application"]
