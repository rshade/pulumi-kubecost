"""A Kubernetes Python Pulumi program"""

import pulumi
from pulumi import ResourceOptions
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs, Namespace
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts

# Create Kubecost Namespace: kubectl create namespace kubecost
kubecostNameSpace = Namespace("kubecost")
# Deploy kubecost from yaml
#helm repo add kubecost https://kubecost.github.io/cost-analyzer/
#helm install kubecost kubecost/cost-analyzer --namespace kubecost --set kubecostToken="cmljaGFyZC5zaGFkZUBnbWFpbC5jb20=xm343yadf98"
kubecost = Chart(
  'kubecost',
  ChartOpts(
    fetch_opts={'repo': 'https://kubecost.github.io/cost-analyzer/'},
    chart='cost-analyzer',
    namespace= kubecostNameSpace._name,
    values={
      "kubecostToken": "cmljaGFyZC5zaGFkZUBnbWFpbC5jb20=xm343yadf98"
    }
  ),
  opts=ResourceOptions(depends_on=[kubecostNameSpace])
)
