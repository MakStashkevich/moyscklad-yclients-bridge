FROM python:3.10

LABEL maintainer="Maksim Stashkevich <makstashkevich@gmail.com>"

WORKDIR /bridge

COPY ./requirements.txt /bridge/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /bridge/requirements.txt

COPY . /bridge/

#EXPOSE 8080
EXPOSE 3000

ENTRYPOINT ["python", "-m", "bridge"]