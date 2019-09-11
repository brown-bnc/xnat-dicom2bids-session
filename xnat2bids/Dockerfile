FROM python:2.7.14-alpine3.6

RUN pip install \
        docopt \
    && \
    rm -r ${HOME}/.cache/pip

ADD xnat2bids.py /usr/local/bin
