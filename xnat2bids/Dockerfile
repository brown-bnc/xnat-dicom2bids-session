FROM python:2.7.14-alpine3.6

RUN pip install \
        docopt \
    && \
    rm -r ${HOME}/.cache/pip

COPY xnat2bids/xnat2bids.py /usr/local/bin

RUN chmod +x /usr/local/bin/xnat2bids.py
