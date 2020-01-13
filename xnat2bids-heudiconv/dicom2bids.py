def get_image_data():
    if project is None or subject is None:
        # Get project ID and subject ID from session JSON
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


def build_bids_map():
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


def main():

    


if __name__ == "__main__":
   mai()