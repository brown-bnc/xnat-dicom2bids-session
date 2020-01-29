FROM nipy/heudiconv:0.5.4

RUN  mkdir -p /opt/src/bids
COPY xnat2bids-heudiconv/src/* /opt/src/bids/
COPY xnat2bids-heudiconv/xnat_command.sh /opt/src/bids/xnat_command.sh

WORKDIR /opt/src
