# Submit kubeflow pipelines to do inference in dijet samples

## Create a docker image with the evaluation script (only if image doesn't already exists)

If ```spanet_dijets_eval.py``` was modified, create a new docker image (otherwise, use ```gitlab-registry.cern.ch/jbossios/docker-images/atlas-spanet-jona-dijets-eval```).

Run the following to create a new docker image (change ```CUSTOM``` accordingly):

```
sudo docker login gitlab-registry.cern.ch
sudo docker build . -f Dockerfile -t gitlab-registry.cern.ch/jbossios/docker-images/CUSTOM
sudo docker push gitlab-registry.cern.ch/jbossios/docker-images/CUSTOM
```

Repository with docker images: https://gitlab.cern.ch/jbossios/docker-images

## Create yaml files (one per pipeline)

Get Python3.8+:

```
source Setup.sh
```

Set the following in ```create_yaml.py```

- ```path```: path to dijet H5 files
- ```n_steps_per_file```: number of steps/jobs per yaml file
- ```versions```: list of SPANet's versions

Run script:

```
python create_yaml.py
```

## Submit kubeflow pipelines

### Create kerberos ticket

On a notebook terminal run the following:

````
kubectl delete secret krb-secret
kinit USERNAME
kubectl create secret generic krb-secret --from-file=/tmp/krb5cc_1000
```

#### Submit a pipeline using ml.cern.ch

1. Go to https://ml.cern.ch/_/pipeline/?
2. Follow the '+ Upload pipeline' link.
3. Define ```Pipeline Name``` (must be unique)
4. Set ```Pipeline Description``` to ```namespace: jonathan-bossio```
5. Upload yaml file and click ```create```

#### Submit pipelines with kfp


