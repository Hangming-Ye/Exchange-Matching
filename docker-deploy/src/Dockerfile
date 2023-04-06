FROM ubuntu:20.04
RUN apt-get update && apt-get install libpq-dev python-dev python3-pip -y
RUN mkdir src
WORKDIR /src
ADD . /src
RUN pip3 install -r /src/requirements.txt
RUN chmod 777 run.sh