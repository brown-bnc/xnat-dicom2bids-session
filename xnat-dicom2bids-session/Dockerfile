FROM python:3.7

RUN apt-get update && apt-get install -y curl zip pigz

RUN pip install pydicom nipype requests && \
    rm -r ${HOME}/.cache/pip 

RUN cd /opt && \
    curl -L https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20190410/dcm2niix_11-Apr-2019_lnx.zip  > dcm2niix.zip && \
    unzip dcm2niix.zip && \
    mv dcm2niix /usr/local/bin && \
    chmod a+x /usr/local/bin/dcm2niix && \
    rm dcm* 

RUN  mkdir -p /opt/src
COPY xnat-dicom2bids-session/dicom2bids.py /opt/src/dicom2bids.py

RUN apt-get remove -y curl zip && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/src
