from argparse import ArgumentParser
from typing import Optional
from numpy import ndarray as Array

import h5py
import os

# Copy kerberos secret
os.system('cp /secret/krb-secret-vol/krb5cc_1000 /tmp/krb5cc_1000')
os.system('chmod 600 /tmp/krb5cc_1000')
os.system('cp /secret/krb-secret-vol/krb5cc_1000 /tmp/krb5cc_0')
os.system('chmod 600 /tmp/krb5cc_0')

# Import SPANet
import sys
sys.path.insert(1, '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_Anthony/SPANet/')

# Get arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', action='store', dest='input_file_name', default='')
parser.add_argument('-v', action='store', dest='version', default='')
parser.add_argument('-s', action='store', dest='sample', default='', help='options: Signal, Dijets')
args = parser.parse_args()

# Protections
if not args.input_file_name:
    print('ERROR: no input file name was provided, exiting')
    sys.exit(1)
if not args.version:
    print('ERROR: no version was provided, exiting')
    sys.exit(1)

input_file_name = args.input_file_name
version = args.version
sample = args.sample

# Global settings
EVENT_FILE = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_Anthony/SPANet/event_files/signal.ini'
LOG_DIR = f'/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_outputs/version_{version}'
OUT_PATH = f'/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/ML_Pipelines_{sample}_Outputs/'

# Create output folder
output_path = f'{OUT_PATH}v{version}'
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Run SPANet's evaluation
command = f'python3 evaluate.py -l {LOG_DIR} -v {sample}_{version} -i {input_file_name} -o {output_path}'
print(command)
os.system(command)
