FROM gitlab-registry.cern.ch/ai-ml/kubeflow_images/atlas-pytorch-gpu:0183442cdb7ad58434d6626b2ac6ff2befffa9a9

COPY spanet_dijets_eval.py /spanet_dijets_eval.py
COPY spanet_signal_eval.py /spanet_signal_eval.py
COPY spanet_eval_on_pipelines.py /spanet_eval_on_pipelines.py
