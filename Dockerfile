FROM python:3.10

LABEL maintainer="Maksim Stashkevich <makstashkevich@gmail.com>"

WORKDIR /bridge

COPY ./requirements.txt /bridge/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /bridge/requirements.txt

COPY . /bridge/

VOLUME "./bridge.session:/bridge/bridge.session"

ENTRYPOINT ["python", "-m", "bridge"]