# dicom2bids-session

For a given XNAT session, this container will convert all dicoms to nifti and it will generate JSON BIDS side car.
This container **does not** organize the files in a BIDS's ready directory.

In order to use BID's apps in XNAT, as set-upt command is used to organize the output of this conatiner in a BIDS-compatible directory.

This container is based on XNAT's [original](https://github.com/NrgXnat/docker-images/tree/master/dcm2bids-session) with the following modifications:

* The dicom2bids.py has been modified from the [original](https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py) to run on Python 3 and use PyDicom instead dicom as the later is depracated.
* dicom2bids.py expects the bidsmap.json file to be uploaded as a resouce to the project under the following path /resources/bids-config/bidsmap.json

## Building 

From parent directory run:

```
./build_docker.sh -f -t v0.1.0 dicom2bids-session
```