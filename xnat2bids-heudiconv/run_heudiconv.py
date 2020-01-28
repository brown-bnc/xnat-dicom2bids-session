


import subprocess
import sys
from xnat_utils import *

def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)

    #get PI from project name
    investigator = project.lower().split('_')[0] 

     # Paths to export source data in a BIDS friendly way
    study_prefix = "study-" + project.lower().split('_')[1]
    subject_prefix = "sub-" + subject.lower()
    session_prefix = "ses-"+ session.lower()

    bids_study_dir = os.path.join(bids_root_dir, investigator, study_prefix)
    bids_subject_dir = os.path.join(bids_study_dir, "xnat-export", subject_prefix)
    bids_session_dir = os.path.join(bids_subject_dir, session_prefix)

    stdout_file = open('bids_session_dir/stdout_file.log', 'a')
    stderr_file = open('bids_session_dir/stderr_file.log', 'a') 
    heudi_cmd = shlex.split( "heudiconv -f reproin --bids \
                              -o /data/xnat-dev/bids-export/sanes/study-sadlum/rawdata/ \
                              --dicom_dir_template /data/xnat-dev/bids-export/sanes/study-sadlum/sourcedata/sub-{subject}/ses-{session}/*/*.dcm \
                              --subjects bidstest --ses xnat_dev_e00009"
    process = subprocess.Popen(['ping', '-c 4', 'python.org'], 
                        stdout = stdout_file,
                        stderr = stderr_file,
                        universal_newlines = True)

    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines():
                print(output.strip())
            break



def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()