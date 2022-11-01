FROM python:3.10

LABEL maintainer="Maksim Stashkevich <makstashkevich@gmail.com>"

WORKDIR /bridge

COPY ./requirements.txt /bridge/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /bridge/requirements.txt

COPY . /bridge/

EXPOSE 7080

ENTRYPOINT ["python", "-m", "bridge"]