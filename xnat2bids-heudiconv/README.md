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

```
python dicom_simlink_dump.py --host http://bnc.brown.edu/xnat-dev --user admin --password admin --subject BIDSTEST --session XNAT_DEV_E00009 --project SANES_SADLUM --bids_root_dir /data/xnat-dev/bids-export
```


<!-- http://bnc.brown.edu/xnat-dev/app/action/DisplayItemAction/search_element/xnat%3AmrSessionData/search_field/xnat%3AmrSessionData.ID/search_value/XNAT_DEV_E00009/popup/false/project/SANES_SADLUM -->