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
COPY dicom2bids.py /opt/src/dicom2bids.py

RUN apt-get remove -y curl zip && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/src

# LABEL org.nrg.commands="[{\"inputs\": [{\"command-line-flag\": \"--session\", \"name\": \"session_id\", \"required\": true, \"replacement-key\": \"#SESSION_ID#\", \"type\": \"string\", \"description\": \"XNAT ID of the session\"}, {\"command-line-flag\": \"--session\", \"name\": \"session_id\", \"required\": true, \"replacement-key\": \"#SESSION_ID#\", \"type\": \"string\", \"description\": \"XNAT ID of the session\"}, {\"command-line-flag\": \"--overwrite\", \"name\": \"overwrite\", \"default-value\": false, \"false-value\": \"False\", \"required\": false, \"true-value\": \"True\", \"replacement-key\": \"#OVERWRITE#\", \"type\": \"boolean\", \"description\": \"Overwrite any existing NIFTI and BIDS scan resources?\"}], \"workdir\": \"/src\", \"name\": \"dcm2bids-session\", \"command-line\": \"python dcm2bids.py #SESSION_ID# #OVERWRITE# --host \$XNAT_HOST --user \$XNAT_USER --pass \$XNAT_PASS --upload-by-ref False --dicomdir /dicom --niftidir /nifti\", \"outputs\": [], \"image\": \"bnc/xnat-dcm2bids-session:1.5\", \"override-entrypoint\": true, \"version\": \"1.5.1\", \"schema-version\": \"1.0\", \"xnat\": [{\"derived-inputs\": [{\"provides-value-for-command-input\": \"session_id\", \"name\": \"session-id\", \"derived-from-xnat-object-property\": \"id\", \"derived-from-wrapper-input\": \"session\", \"type\": \"string\", \"description\": \"The session's id\"}], \"contexts\": [\"xnat:imageSessionData\"], \"description\": \"Run dcm2niix-session on a Session\", \"output-handlers\": [], \"external-inputs\": [{\"required\": true, \"type\": \"Session\", \"name\": \"session\", \"description\": \"Input session\"}], \"name\": \"dcm2bids-session-session\"}], \"mounts\": [{\"writable\": \"true\", \"path\": \"/nifti\", \"name\": \"nifti\"}], \"type\": \"docker\", \"description\": \"Runs dcm2niix on a session's scans, and uploads the nifti and bids json\"}]"