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
args = parser.parse_args()

if not args.input_file_name:
    print('ERROR: no input file name was provided, exiting')
    sys.exit(1)

input_file_name = args.input_file_name

VERSION = 69 # trained with 1.4 TeV UDS+UDB full+partial events and using max8jets
OUT_PATH = '/eos/atlas/atlaslocalgroupdisk/susy/jbossios_rpv_mj/Testing_ML_Pipelines/'
EVENT_FILE = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_package/SPANet/event_files/signal.ini'
gpu = False # Temporary

def create_hdf5_output(output_file: str,
                       dataset: JetReconstructionDataset,
                       full_predictions: Array,
                       full_classifications: Array):
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
    
rtags = ['r9364', 'r10201', 'r10724']
splits = input_file_name.split('.')
dsid = splits[2]
rtag = [tag for item in splits for tag in rtags if tag in item][0]
extension = '.'.join(splits[4:6])

output_file = f'{output_path}/dijets_v{VERSION}_output_{dsid}_{rtag}_{extension}.h5'

batch_size = None

print(f'{log_dir = }')
print(f'{test_file = }')
print(f'{EVENT_FILE = }')
print(f'{batch_size = }')
print(f'{gpu = }')
model = load_model(log_dir, test_file, EVENT_FILE, batch_size, gpu)

full_predictions, full_classifications, *_ = predict_on_test_dataset(model, gpu)
    
create_hdf5_output(output_file, model.testing_dataset, full_predictions, full_classifications)  