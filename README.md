# Submit kubeflow pipelines to do inference in dijet samples

## Create a docker image with the evaluation script (only if image doesn't already exists)

If ```spanet_dijets_eval.py``` was modified, create a new docker image, otherwise select one of the following images:

- ```gitlab-registry.cern.ch/jbossios/docker-images/atlas-spanet-jona-dijets-eval```: first working image (old inputs)
- ```gitlab-registry.cern.ch/jbossios/docker-images/atlas-spanet-jona-eval-all```: latest image (first time supporting signal inputs)

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

On a notebook terminal run the following*:

```
kubectl delete secret krb-secret
kinit USERNAME
kubectl create secret generic krb-secret --from-file=/tmp/krb5cc_1000
```

### Get SPANet

```
cp -r /eos/atlas/atlascerngroupdisk/phys-susy/RPV_mutlijets_ANA-SUSY-2019-24/spanet_jona/SPANET_package_backup_notebook/SPANet .
cd SPANet/
```

* To open a jupyter notebook on Kubeflow, follow these steps:

1. ssh -D 8090 lxplus.cern.ch
2. google-chrome --proxy-server=socks5://127.0.0.1:8090
3. Go to https://ml.cern.ch
4. Create a notebook using 1 GPU and the following image: gitlab-registry.cern.ch/ai-ml/kubeflow_images/atlas-pytorch-gpu:0183442cdb7ad58434d6626b2ac6ff2befffa9a9

#### Submit a pipeline using ml.cern.ch

1. Go to https://ml.cern.ch/_/pipeline/?
2. Follow the '+ Upload pipeline' link.
3. Define ```Pipeline Name``` (must be unique)
4. Set ```Pipeline Description``` to ```namespace: jonathan-bossio```
5. Upload yaml file and click ```create```
6. After new page is loaded, click ```+ Create run```
7. Choose experiment and click ```Start```
8. Monitor pipeline under Pipelines > Experiments

#### Submit pipelines with kfp

The ```submit_pipelines.py``` script should be already present (but if it is outdated, clone this repo or copy here new version)

Set the following in ```submit_pipelines.py```:

- ```date```: should match the date of the yaml files
- ```n_yaml_files_per_version```: should match the number of yaml files created per SPANet's versions
- ```sample_type```: signal or dijets
- ```versions```: SPANet versions to use

Submit pipelines with the following (inside a kubeflow jupyter notebook):

```
python3 submit_pipelines.py
```

Pipelines can be monitored on https://ml.cern.ch (Pipelines > Experiments)

### How to terminate pipelines with kfp

#### Get list of pipelines with Python

```
import kfp
client = kfp.Client()
print([pipeline.name for pipeline in client.list_pipelines().pipelines])
```

Delete the pipeline of your choice with the following

```
client.delete_pipeline(client.get_pipeline_id("PIPELINE_NAME"))
```

### How to get the log from a pipeline on a Jupyter notebook

1. Get list of workflows

```
kubectl -n jonathan-bossio get workflows
```

2. List pods from a workflow (example for spanet-dijets-eval-23022022-69hzrc5)

```
kubectl -n jonathan-bossio get pods | grep spanet-dijets-eval-23022022-69hzrc5
```

3. Get log for a given pod (example for pod spanet-dijets-eval-23022022-69hzrc5-918158780)

```
kubectl -n jonathan-bossio logs spanet-dijets-eval-23022022-69hzrc5-918158780 main
```
