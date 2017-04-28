FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl software-properties-common
RUN add-apt-repository ppa:fkrull/deadsnakes && apt-get update
RUN apt-get install -qq -y \
    python2.3 \
    python2.4 \
    python2.7 \
    python3.3 \
    python3.4 \
    python3.5 \
    python3.6 \
    pypy
ADD pomsky.py /
ADD test.sh /
ADD workingfile.txt /
CMD [ "./test.sh" ]
