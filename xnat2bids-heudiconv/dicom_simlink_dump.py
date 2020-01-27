'''
Filename: xnat2bids-heudiconv/dicom_simlink_dump.py
Created Date: Friday, December 6th 2019, 2:28:10 pm
Author: Isabel Restrepo

Export XNAT DICOM SCANS as symlinks to the Resources folder for BIDS

Copyright (c) 2019 Brown University
'''

'''
Filename: /dicom2bids.py
Path: xnat-dicom2bids-session
Created Date: Monday, August 26th 2019, 10:12:40 am
Maintainer: Isabel Restrepo
Descriptyion: Export a XNAT session into BIDS directory format


Original file lives here: https://bitbucket.org/nrg_customizations/nrg_pipeline_dicomtobids/src/default/scripts/catalog/DicomToBIDS/scripts/dcm2bids_wholeSession.py
'''

import argparse
import logging


import collections
import json
import requests
import os
import glob
import sys
import subprocess
import time
import zipfile
import tempfile
import pydicom
from shutil import copy as fileCopy
from collections import OrderedDict
import requests.packages.urllib3
import six
from six.moves import zip
requests.packages.urllib3.disable_warnings()


def cleanServer(server):
    server.strip()
    if server[-1] == '/':
        server = server[:-1]
    if server.find('http') == -1:
        server = 'https://' + server
    return server


def isTrue(arg):
    return arg is not None and (arg == 'Y' or arg == '1' or arg == 'True')


def download(name, pathDict):
    if os.access(pathDict['absolutePath'], os.R_OK):
        print("We have local OS access")
        fileCopy(pathDict['absolutePath'], name)
        print('Copied %s.' % pathDict['absolutePath'])
    else:
        with open(name, 'wb') as f:
            r = get(pathDict['URI'], stream=True)

            for block in r.iter_content(1024):
                if not block:
                    break

                f.write(block)
        print('Downloaded remote file %s.' % name)


def parse_args(**kwargs):
    parser = argparse.ArgumentParser(description="Dump DICOMS to a BIDS firendly sourcedata directory")
    parser.add_argument("--host", default="https://cnda.wustl.edu", help="CNDA host", required=True)
    parser.add_argument("--user", help="CNDA username", required=True)
    parser.add_argument("--password", help="Password", required=True)
    parser.add_argument("--session", help="Session ID", required=True)
    parser.add_argument("--subject", help="Subject Label", required=False)
    parser.add_argument("--project", help="Project", required=False)
    parser.add_argument("--bids_root_dir", help="Root output directory for BIDS files", required=True)
    # parser.add_argument("--overwrite", help="Overwrite NIFTI files if they exist")
    parser.add_argument('--version', action='version', version='%(prog)s 1')

    args, unknown_args = parser.parse_known_args()
    host = cleanServer(args.host)
    session = args.session
    subject = args.subject
    project = args.project
    overwrite = isTrue(args.overwrite)
    dicomdir = args.dicomdir

    builddir = os.getcwd()

    # Set up working directory
    if not os.access(bids_root_dir, os.R_OK):
        print('Making BIDS directory %s' % bids_root_dir)
        os.mkdir(bids_root_dir)

    # Set up session
    sess = requests.Session()
    sess.verify = False
    sess.auth = (args.user, args.password)

    return sess


def get(url, **kwargs):
    try:
        r = sess.get(url, **kwargs)
        r.raise_for_status()
    except (requests.ConnectionError, requests.exceptions.RequestException) as e:
        print("Request Failed")
        print("    " + str(e))
        sys.exit(1)
    return r


def get_project_and_subject_id(project, subject, session):
    """Get project ID and subject ID from session JSON
       If calling within XNAT, only session is passed"""
    print("Get project and subject ID for session ID %s." % session)
    r = get(host + "/data/experiments/%s" % session, params={"format": "json", "handler": "values", "columns": "project,subject_ID"})
    sessionValuesJson = r.json()["ResultSet"]["Result"][0]
    project = sessionValuesJson["project"] if project is None else project
    subjectID = sessionValuesJson["subject_ID"]
    print("Project: " + project)
    print("Subject ID: " + subjectID)

    if subject is None:
        print()
        print("Get subject label for subject ID %s." % subjectID)
        r = get(host + "/data/subjects/%s" % subjectID, params={"format": "json", "handler": "values", "columns": "label"})
        subject = r.json()["ResultSet"]["Result"][0]["label"]
        print("Subject label: " + subject)

    return project, subject

def get_scan_id_and description_list(session):

    # Get list of scan ids
    print("Get scan list for session ID %s." % session)
    r = get(host + "/data/experiments/%s/scans" % session, params={"format": "json"})
    scanRequestResultList = r.json()["ResultSet"]["Result"]
    scanIDList = [scan['ID'] for scan in scanRequestResultList]
    seriesDescList = [scan['series_description'] for scan in scanRequestResultList]  # { id: sd for (scan['ID'], scan['series_description']) in scanRequestResultList }
    print('Found scans %s.' % ', '.join(scanIDList))
    print('Series descriptions %s' % ', '.join(seriesDescList))

    # Fall back on scan type if series description field is empty
    if set(seriesDescList) == set(['']):
        seriesDescList = [scan['type'] for scan in scanRequestResultList]
        print('Fell back to scan types %s' % ', '.join(seriesDescList))

    return scanIDList, seriesDescList

def populate_bidsmap():
    # Read bids map from input config
    bidsmaplist = []

    print("Get project BIDS map if one exists")
    # We don't use the convenience get() method because that throws exceptions when the object is not found.
    r = sess.get(host + "/data/projects/%s/resources/config/files/bidsmap.json" % project, params={"contents": True})
    if r.ok:
        bidsmaptoadd = r.json()
        print("BIDS bidsmaptoadd: ",  bidsmaptoadd)
        for mapentry in bidsmaptoadd:
            if mapentry not in bidsmaplist:
                bidsmaplist.append(mapentry)
    else:
        print("Could not read project BIDS map")


    # Get site-level configs
    print("Get Site BIDS map ")
    # We don't use the convenience get() method because that throws exceptions when the object is not found.
    r = sess.get(host + "/data/config/bids/bidsmap", params={"contents": True})
    if r.ok:
        bidsmaptoadd = r.json()
        print("BIDS bidsmaptoadd: ",  bidsmaptoadd)
        for mapentry in bidsmaptoadd:
            if mapentry not in bidsmaplist:
                bidsmaplist.append(mapentry)
    else:
        print("Could not read site-wide BIDS map")

    print("BIDS bidsmaplist: ", json.dumps(bidsmaplist))

    # Collapse human-readable JSON to dict for processing
    bidsnamemap = {x['series_description'].lower(): x['bidsname'] for x in bidsmaplist if 'series_description' in x and 'bidsname' in x}

    # Map all series descriptions to BIDS names (case insensitive)
    resolved = [bidsnamemap[x.lower()] for x in seriesDescList if x.lower() in bidsnamemap]

    # Count occurrences
    bidscount = collections.Counter(resolved)

    # Remove multiples
    multiples = {seriesdesc: count for seriesdesc, count in six.viewitems(bidscount) if count > 1}



def assign_bids_name(subject, scanIDList, seriesDescList, build_dir, study_bids_dir):
    """
        subject: Subject to process
        scanIDList: ID List of scans 
        seriesDescList: List of series descriptions
        build_dir: build director. What is this?
        study_bids_dir: BIDS directory to copy simlinks to. Typically the RESOURCES/BIDS
    """
    
    # Paths to export source data in a BIDS friendly way
    base = "sub-" + subject + "_"
    bids_subject_dir = os.path.join(study_bids_dir, "sourcedata", subject)
    bids_session_dir = os.path.join(bids_subject_dir, "ses-"+ session)

    # Cheat and reverse scanid and seriesdesc lists so numbering is in the right order
    for scanid, seriesdesc in zip(reversed(scanIDList), reversed(seriesDescList)):

        print('Beginning process for scan %s.' % scanid)
        os.chdir(build_dir)
        print('Assigning BIDS name for scan %s.' % scanid)

        #We use the bidsmap to correct miss-labeled series at the scanner.
        #otherwise we assume decription is correct and let heudiconv tdo the work
        if seriesdesc.lower() not in bidsnamemap:
            print("Series " + seriesdesc + " not found in BIDSMAP")
            # bidsname = "Z"
            # continue  # Exclude series from processing
            match = seriesdesc.lower()
        else:
            print("Series " + seriesdesc + " matched " + bidsnamemap[seriesdesc.lower()])
            match = bidsnamemap[seriesdesc.lower()]

        bidsname = match

        # Get scan resources
        print("Get scan resources for scan %s." % scanid)
        r = get(host + "/data/experiments/%s/scans/%s/resources" % (session, scanid), params={"format": "json"})
        scanResources = r.json()["ResultSet"]["Result"]
        print('Found resources %s.' % ', '.join(res["label"] for res in scanResources))

        dicomResourceList = [res for res in scanResources if res["label"] == "DICOM"]

        if len(dicomResourceList) == 0:
            print("Scan %s has no DICOM resource." % scanid)
            # scanInfo['hasDicom'] = False
            continue
        elif len(dicomResourceList) > :
            print("Scan %s has more than one DICOM resource Skipping." % scanid)
            # scanInfo['hasDicom'] = False
            continue

        dicomResource = dicomResourceList[0] if len(dicomResourceList) > 0 else None

        usingDicom = True if (len(dicomResourceList) == 1) else False

        if dicomResource is not None and dicomResource["file_count"]:
            if int(dicomResource["file_count"]) == 0:
                print("DICOM resource for scan %s has no files. Skipping." % scanid)
                continue
        else:
            print("DICOM resources for scan %s have a blank \"file_count\", so I cannot check to see if there are no files. I am not skipping the scan, but this may lead to errors later if there are no files." % scanid)

        # BIDS sourcedatadirectory for this scan
        bids_scan_directory = os.path.join(bids_session_dir, bidsname)

        if not os.path.isdir(bids_scan_directory):
            print('Making scan DICOM directory %s.' % bids_scan_directory)
            os.mkdir(bids_scan_directory)
        
        # For now exit if directory is not empty
        for f in os.listdir(bids_scan_directory):
            print("Output Directory is not empty. Skipping.")
                continue
            # os.remove(os.path.join(bids_scan_directory, f))

        # Deal with DICOMs
        print('Get list of DICOM files for scan %s.' % scanid)

        if usingDicom:
            filesURL = host + "/data/experiments/%s/scans/%s/resources/DICOM/files" % (session, scanid)
        
        r = get(filesURL, params={"format": "json"})
        # Build a dict keyed off file name
        dicomFileDict = {dicom['Name']: {'URI': host + dicom['URI']} for dicom in r.json()["ResultSet"]["Result"]}

        print("**********")
        print(dicomFileDict)
        print("**********")

        # Have to manually add absolutePath with a separate request
        r = get(filesURL, params={"format": "json", "locator": "absolutePath"})
        for dicom in r.json()["ResultSet"]["Result"]:
            dicomFileDict[dicom['Name']]['absolutePath'] = dicom['absolutePath']

        # Download DICOMs
        print("Downloading files for scan %s." % scanid)
        os.chdir(bids_scan_directory)

        # Check secondary
        # Download any one DICOM from the series and check its headers
        # If the headers indicate it is a secondary capture, we will skip this series.
        dicomFileList = list(dicomFileDict.items())

        (name, pathDict) = dicomFileList[0]
        download(name, pathDict)

        if usingDicom:
            print('Checking modality in DICOM headers of file %s.' % name)
            d = pydicom.dcmread(name)
            modalityHeader = d.get((0x0008, 0x0060), None)
            if modalityHeader:
                print('Modality header: %s' % modalityHeader)
                modality = modalityHeader.value.strip("'").strip('"')
                if modality == 'SC' or modality == 'SR':
                    print('Scan %s is a secondary capture. Skipping.' % scanid)
                    continue
            else:
                print('Could not read modality from DICOM headers. Skipping.')
                continue

        # Download remaining DICOMs
        for name, pathDict in dicomFileList[1:]:
            download(name, pathDict) 

        os.chdir(build_dir)
        print('Done downloading for scan %s.' % scanid)
    
def main():
    sess, session, project, subject, bids_root_dir = parse_args()
    
    if project is None or subject is None:
        project, subject = get_project_and_subject_id(session) 
    
    scanIDList, seriesDescList = get_scan_ids(session)
    
    #get PI from project name
    investigator = project.lower().split('-')[0] 

    bids_study_dir = os.path.join(bids_root_dir, investigator, project)

    # Set up working directory
    if not os.access(bids_study_dir, os.R_OK):
        print('Making BIDS directory %s' % bids_study_dir)
        os.mkdir(bids_study_dir)

    assign_bids_name(subject, scanIDList, seriesDescList, build_dir, bids_study_dir)