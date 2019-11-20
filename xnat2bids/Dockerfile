FROM python:3.7

RUN pip install \
        docopt \
    && \
    rm -r ${HOME}/.cache/pip

COPY xnat2bids/xnat2bids.py /usr/local/bin

RUN chmod +x /usr/local/bin/xnat2bids.py
