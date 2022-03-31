"""A Kubernetes Python Pulumi program"""

from pulumi import ResourceOptions, Config, Output
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs, Namespace, Secret
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts
from pulumi_kubernetes_ingress_nginx import IngressController, ControllerArgs, ControllerPublishServiceArgs

# Create Kubecost Namespace: kubectl create namespace kubecost
kubecostNameSpace = Namespace(
  "kubecost",
  metadata=ObjectMetaArgs(
    name="kubecost"
  )
)
# Deploy kubecost from yaml
#helm repo add kubecost https://kubecost.github.io/cost-analyzer/
#helm install kubecost kubecost/cost-analyzer --namespace kubecost --set kubecostToken="cmljaGFyZC5zaGFkZUBnbWFpbC5jb20=xm343yadf98"
kubecost = Chart(
  'kubecost',
  ChartOpts(
    fetch_opts={'repo': 'https://kubecost.github.io/cost-analyzer/'},
    chart='cost-analyzer',
    namespace= kubecostNameSpace.id,
    values={
      "kubecostToken": "cmljaGFyZC5zaGFkZUBnbWFpbC5jb20=xm343yadf98",
    }
  ),
  opts=ResourceOptions(depends_on=[kubecostNameSpace])
)

kubecostIngressSecret = Secret(
  "kubecost-auth",
  metadata=ObjectMetaArgs(
    name="kubecost-auth",
    namespace=kubecostNameSpace.id,
  ),
  string_data={
    "auth": "YWRtaW46JGFwcjEkZ2tJenJxU2ckMWx3RUpFN1lFcTlzR0FNN1VtR1djMAo="
  },
)
# Install the NGINX ingress controller to our cluster. The controller
# consists of a Pod and a Service. Install it and configure the controller
# to publish the load balancer IP address on each Ingress so that
# applications can depend on the IP address of the load balancer if needed.
ctrl = IngressController(
  'kubecost',
  controller=ControllerArgs(
      publish_service=ControllerPublishServiceArgs(
          enabled=True,
      ),
  ),
)
# Use a nginx ingress controller instead
kubcostIngress = kubernetes.networking.v1.Ingress(
  "kubecost-ingress",
  metadata=kubernetes.meta.v1.ObjectMetaArgs(
    name="kubecost-ingress",
    namespace=kubecostNameSpace.id,
    labels={
      "app": "kubecost",
    },
    annotations={
        "nginx.ingress.kubernetes.io/auth-type": "basic",
        "nginx.ingress.kubernetes.io/auth-secret": kubecostIngressSecret.id,
        "nginx.ingress.kubernetes.io/auth-realm": "Authentication Required - ok",
    },
  ),
  spec={
    'rules': [
          {
              # Replace this with your own domain!
              'http': {
                  'paths': [{
                      'pathType': 'Prefix',
                      'path': '/',
                      'backend': {
                          'service': {
                              'name': "kubecost-cost-analyzer",
                              'port': { 'number': 9090 },
                          },
                      },
                  }],
              },
          },
    ]
  },
# spec=kubernetes.networking.v1.IngressSpecArgs(
#     default_backend=kubernetes.networking.v1.IngressBackendArgs(
#       service=kubernetes.networking.v1.IngressServiceBackendArgs(
#         name="kubecost-cost-analyzer",
#         port=kubernetes.networking.v1.ServiceBackendPortArgs(
#           number=9090,
#         )
#       )
#     )
#   ),
  opts=ResourceOptions(depends_on=[kubecost, kubecostIngressSecret])
)
