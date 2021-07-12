FROM ubuntu:bionic

RUN apt-get update && apt-get install -y --no-install-recommends dialog apt-utils
RUN apt-get -y install grep coreutils util-linux progress python3-pip git
RUN python3 -m pip install -U pip
RUN python3 -m pip install pytest

WORKDIR /workdir

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/workdir/entrypoint.sh"]
