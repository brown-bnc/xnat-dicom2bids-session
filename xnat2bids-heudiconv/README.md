## Testing

In remote

### Checkout source
```
cd maintain/src
git clone https://github.com/brown-bnc/xnat-docker-plugins.git
```

### Pull docker 

```
docker pull brownbnc/xnat2bids-heudiconv:v0.1.0
```

### Run with source and needed volumes


```
docker run --rm -it --entrypoint /bin/bash  \
           -v /maintain/src/xnat-docker-plugins/xnat2bids-heudiconv/:/opt/src/bids/ \
           -v /mnt/brownresearch/xnat-dev/bids-export/:/data/xnat-dev/bids-export \
           --name xnat2bids-heudiconv brownbnc/xnat2bids-heudiconv:v0.1.0 

```


### Run script

#### Export dicoms
```
python dicom_simlink_dump.py --host http://bnc.brown.edu/xnat-dev --user admin --password admin --subject BIDSTEST --session XNAT_DEV_E00009 --project SANES_SADLUM --bids_root_dir /data/xnat-dev/bids-export
```
#### Convert to BIDS
heudiconv -f reproin --bids -o /data/xnat-dev/bids-export/sanes/study-sadlum/rawdata/sub-bidstest/ses-xnat_dev_e00009 --files /data/xnat-dev/bids-export/sanes/study-sadlum/sourcedata/sub-bidstest/ses-xnat_dev_e00009 -c none

<!-- http://bnc.brown.edu/xnat-dev/app/action/DisplayItemAction/search_element/xnat%3AmrSessionData/search_field/xnat%3AmrSessionData.ID/search_value/XNAT_DEV_E00009/popup/false/project/SANES_SADLUM -->


heudiconv -f reproin --bids -o /data/xnat-dev/bids-export/sanes/study-sadlum/rawdata/ --dicom_dir_template /data/xnat-dev/bids-export/sanes/study-sadlum/sourcedata/sub-{subject}/ses-{session}/*/*.dcm --subjects bidstest --ses xnat_dev_e00009  -c none

heudiconv -f reproin --bids -o /data/xnat-dev/bids-export/sanes/study-sadlum/rawdata/ --files /data/xnat-dev/bids-export/sanes/study-sadlum/sourcedata/sub-bidstest/ses-xnat_dev_e00009 -c none