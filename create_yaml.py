path = '/eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/ntuples/tag/input/mc16e/dijets_expanded/python/'
slices = [i for i in range(2, 13)]
date = '23022022'
version = '69'

###############################################################
# DO NOT MODIFY (below this line)
###############################################################

import os

output_file_name = f'spanet_dijets_eval_{date}_v{version}.yaml'
with open(output_file_name, 'w') as ofile:
  ofile.write('apiVersion: argoproj.io/v1alpha1\n')
  ofile.write('kind: Workflow\n')
  ofile.write('metadata:\n')
  ofile.write(f'  generateName: spanet-dijets-eval-{date}-{version}\n')
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
  for jz in slices:
    files = [file_name for file_name in os.listdir(f'{path}JZ{jz}') if file_name.endswith('_spanet.h5')]
    for input_file in files:
      ofile.write("        - { version: '"+version+"', input: '"+path+"JZ"+str(jz)+"/"+input_file+"'}\n")
  ofile.write('  - name: base\n')
  ofile.write('    inputs:\n')
  ofile.write('      parameters:\n')
  ofile.write('      - name: input\n')
  ofile.write('      - name: version\n')
  ofile.write('    retryStrategy:\n')
  ofile.write('      limit: 3\n')
  ofile.write('      retryPolicy: "Always"\n')
  ofile.write('    container:\n')
  ofile.write('      image: gitlab-registry.cern.ch/jbossios/docker-images/atlas-spanet-jona-dijets-final\n')
  ofile.write('      envFrom:\n')
  ofile.write('      - configMapRef:\n')
  ofile.write('          name: userid-configmap\n')
  ofile.write('      volumeMounts:\n')
  ofile.write('      - name: eos\n')
  ofile.write('        mountPath: /eos\n')
  ofile.write('      - name: krb-secret-vol\n')
  ofile.write('        mountPath: /secret/krb-secret-vol\n')
  ofile.write('      resources:\n')
  ofile.write('        limits:\n')
  ofile.write('          memory: "10000Mi"\n')
  ofile.write('        requests:\n')
  ofile.write('          memory: "8000Mi"\n')
  ofile.write('      command: ["/bin/sh","-c"]\n')
  ofile.write('      args: ["python3 /spanet_dijets_eval.py -i {{inputs.parameters.input}} -v {{inputs.parameters.version}}"]\n')

print('>>> ALL DONE <<<')
