#!/bin/bash

echo "------------ EXPORTING DICOMS----------------------------------------"
python dicom_export.py --session $1 --host $2 --user $3 --pass $4 --bids_root_dir /data/xnat/bids-export
echo "------------ RUNNING HEUDICONV---------------------------------------"
python run_heudicon.py --session $1 --host $2 --user $3 --pass $4 --bids_root_dir /data/xnat/bids-export
echo "------------ DONE----------------------------------------------------"

