import os
from datetime import datetime

def create_yaml_files(sample_type, path, version, n_steps_per_file, debug = False):
  """ Create yaml files to evaluate dijets using a given SPANet's network version """

  # Get date
  date = datetime.now().strftime("%d/%m/%Y").replace('/', '')
  #date = '18062022'

  # Create output folder
  output_folder = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_Pipelines_yaml_files/'
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  # Protection
  if not isinstance(version, str):
    version = str(version)

  # Find number of yaml files to be created
  total_steps = sum([1 for folder in os.listdir(path) for file_name in os.listdir(path + folder) if 'user' in folder and file_name.endswith('.root')])
  n_yaml_files = int(total_steps / n_steps_per_file)
  if n_yaml_files * n_steps_per_file < total_steps:
    n_yaml_files += 1

  if debug:
    print('n_steps_per_file = {}'.format(n_steps_per_file))
    print('total_steps = {}'.format(total_steps))
    print('n_yaml_files = {}'.format(n_yaml_files))

  # Separate files into several yaml files
  counter = 1
  yaml_dicts = dict()
  files = [file_name for folder in os.listdir(path) for file_name in os.listdir(path + folder) if 'user' in folder and file_name.endswith('.root')]
  for input_file in files:
    yaml_file_index = int(counter / n_steps_per_file)
    if yaml_file_index * n_steps_per_file < counter:
      yaml_file_index += 1
    if yaml_file_index-1 not in yaml_dicts:
      yaml_dicts[yaml_file_index-1] = [input_file]
    else:
      yaml_dicts[yaml_file_index-1].append(input_file)
    counter += 1

  # Create yaml files
  for yaml_counter in range(n_yaml_files):
    output_file_name = f'{output_folder}spanet_{sample_type}_eval_{date}_v{version}_{yaml_counter}.yaml'
    with open(output_file_name, 'w') as ofile:
      ofile.write('apiVersion: argoproj.io/v1alpha1\n')
      ofile.write('kind: Workflow\n')
      ofile.write('metadata:\n')
      ofile.write(f'  generateName: spanet-{sample_type}-eval-{date}-v{version}-id{yaml_counter}\n')
      ofile.write('spec:\n')
      ofile.write('  entrypoint: main\n')
      ofile.write('  parallelism: 5\n')
      ofile.write('  volumes:\n')
      ofile.write('    - name: eos\n')
      ofile.write('      hostPath:\n')
      ofile.write('        path: /var/eos\n')
      ofile.write('    - name: krb-secret-vol\n')
      ofile.write('      secret:\n')
      ofile.write('        secretName: krb-secret\n')
      ofile.write('    - name: dshm\n')
      ofile.write('      emptyDir:\n')
      ofile.write('        medium: Memory\n')
      ofile.write('  templates:\n')
      ofile.write('  - name: main\n')
      ofile.write('    steps:\n')
      ofile.write('    - - name: inference\n')
      ofile.write('        template: base\n')
      ofile.write('        arguments:\n')
      ofile.write('          parameters:\n')
      ofile.write('          - name: version\n')
      ofile.write('            value: "{{item.version}}"\n')
      ofile.write('          - name: input\n')
      ofile.write('            value: "{{item.input}}"\n')
      ofile.write('        withItems:\n')
      for input_file in yaml_dicts[yaml_counter]:
        ofile.write("        - { version: '"+version+"', input: '"+path+input_file+"'}\n")
      ofile.write('  - name: base\n')
      ofile.write('    inputs:\n')
      ofile.write('      parameters:\n')
      ofile.write('      - name: input\n')
      ofile.write('      - name: version\n')
      ofile.write('    retryStrategy:\n')
      ofile.write('      limit: 3\n')
      ofile.write('      retryPolicy: "Always"\n')
      ofile.write('    container:\n')
      ofile.write('      image: gitlab-registry.cern.ch/jbossios/docker-images/atlas-spanet-jona-evalonroot-19082022\n')
      ofile.write('      envFrom:\n')
      ofile.write('      - configMapRef:\n')
      ofile.write('          name: userid-configmap\n')
      ofile.write('      volumeMounts:\n')
      ofile.write('      - name: eos\n')
      ofile.write('        mountPath: /eos\n')
      ofile.write('      - name: krb-secret-vol\n')
      ofile.write('        mountPath: /secret/krb-secret-vol\n')
      ofile.write('      - name: dshm\n')
      ofile.write('        mountPath: /dev/shm\n')
      ofile.write('      resources:\n')
      ofile.write('        limits:\n')
      ofile.write('          memory: "12000Mi"\n')
      ofile.write('        requests:\n')
      ofile.write('          memory: "10000Mi"\n')
      ofile.write('      command: ["/bin/sh","-c"]\n')
      ofile.write('      args: ["python3 /spanet_eval_on_pipelines.py -i {{inputs.parameters.input}} -v {{inputs.parameters.version}} -s {sample_type}"]\n')


if __name__ == '__main__':
  sample_type = 'Dijets'
  path = {
    'Dijets': '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/ntuples/tag/input/mc16e/dijets/PROD4/',
    'Signal': '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/ntuples/tag/input/mc16e/GG_rpv/PROD2/',
  }[sample_type]
  n_steps = 125
  versions = [str(i) for i in range(97, 98)]
  for version in versions:
    create_yaml_files(sample_type, path, version, n_steps)
  print('>>> ALL DONE <<<')
