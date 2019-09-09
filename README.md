# xnat-docker-plugins

Docker plugins installed for BNC's XNAT instance.

These are inpired by many of the images provided by XNAT [here](https://github.com/NrgXnat/docker-images). We maintain our own copy as we often need some simple changes, updates or different tag versions

## Building the docker image

This rebository provides a convinience script to build and push the desired docker images. For instance to build the dicom2bids-session you can run

```
./docker_build.bash -t 0.1.0 dicom2bids-session
```

In general, the format is as follows.

```
./docker_build.bash [-t NAMED_TAG (optional)] [ image_folder ]
```

### Versioning and tags

The script will always push a tag corresponding to the hash of the git commit. The named tag allows to in addition publish a "prettier" nade tag.


## Testing locally

While these images are created with our JupyterHub set up in mind, you can run them locally 

```
docker run -it brownbnc/dicom2bids-session:0.1.0
```


Or 

Attach a `bash` to session 

```
docker exec /bin/bash brownbnc/dicom2bids-session:0.1.0
```