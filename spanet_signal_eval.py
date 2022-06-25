from argparse import ArgumentParser
from typing import Optional
from numpy import ndarray as Array

import h5py
import os

# Copy Secret
os.system('cp /secret/krb-secret-vol/krb5cc_1000 /tmp/krb5cc_1000')
os.system('chmod 600 /tmp/krb5cc_1000')
os.system('cp /secret/krb-secret-vol/krb5cc_1000 /tmp/krb5cc_0')
os.system('chmod 600 /tmp/krb5cc_0')
os.system('ls /tmp')
os.system('ls /eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_package/SPANet/')

import sys
sys.path.insert(1, '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_package/SPANet/')
from spanet.dataset.jet_reconstruction_dataset import JetReconstructionDataset
from spanet.evaluation import predict_on_test_dataset, load_model

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', action='store', dest='input_file_name', default='')
parser.add_argument('-v', action='store', dest='version', default='')
args = parser.parse_args()

if not args.input_file_name:
    print('ERROR: no input file name was provided, exiting')
    sys.exit(1)
if not args.version:
    print('ERROR: no version was provided, exiting')
    sys.exit(1)

input_file_name = args.input_file_name

VERSION = args.version
OUT_PATH = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/ML_Pipelines_Signal_Outputs/'
EVENT_FILE = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_package/SPANet/event_files/signal.ini'
gpu = False

def create_hdf5_output(output_file: str,
                       dataset: JetReconstructionDataset,
                       full_predictions: Array,
                       full_classifications: Array):
    if os.path.isfile(output_file): # if output file exists, remove it before creating a new one
        os.system('rm {output_file}')
    print(f"Creating output file at: {output_file}")
    with h5py.File(output_file, 'w') as output:
        output.create_dataset(f"source/mask", data=dataset.source_mask)
        for i, (feature_name, _, _) in enumerate(dataset.event_info.source_features):
            output.create_dataset(f"source/{feature_name}", data=dataset.source_data[:, :, i])

        for i, (particle_name, (jets, _)) in enumerate(dataset.event_info.targets.items()):
            output.create_dataset(f"{particle_name}/mask", data=full_classifications[i])
            for k, jet_name in enumerate(jets):
                output.create_dataset(f"{particle_name}/{jet_name}", data=full_predictions[i][:, k])

log_dir = f'/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_outputs/version_{VERSION}'

test_file = input_file_name

# Create output folder
output_path = f'{OUT_PATH}v{VERSION}'
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
#rtags = ['r9364', 'r10201', 'r10724']
#print(f'{input_file_name = }')
#splits = input_file_name.split('.')
#dsid = splits[2]
#tags = splits[3].split('_')
#rtag = [tag for tag in tags if tag in rtags][0]
#extension = '.'.join(splits[4:7])
#output_file = f'{output_path}/signal_v{VERSION}_output_{dsid}_{rtag}_{extension}.h5'

#output_file_name = input_file_name.replace('.h5', f'_spanet_v{VERSION}.h5')
output_file_name = input_file_name.split('/')[-1].replace('.h5', f'_spanet_v{VERSION}.h5')
output_file = f'{output_path}/{output_file_name}'

batch_size = None

print(f'{log_dir = }')
print(f'{test_file = }')
print(f'{EVENT_FILE = }')
print(f'{batch_size = }')
print(f'{output_file = }')
print(f'{gpu = }')
model = load_model(log_dir, test_file, EVENT_FILE, batch_size, gpu, num_workers = 0)

full_predictions, full_classifications, *_ = predict_on_test_dataset(model, gpu)
    
create_hdf5_output(output_file, model.testing_dataset, full_predictions, full_classifications)  
