This page describes a way to deploy OpenShift on top of KubeVirt (in particular when running on OpenShift)

## Requirements

- a kubernetes/openshift cluster
- a valid pull secret
- a connected environment. Disconnected should work by editing the pod definition so that oc and openshift-install are gathered from an existing offline location and stored in /usr/local/bin

## Architecture

- A pod is launched which will deploy an SNO vm and services for api and ingress
- api and ingress route will be created if running on OpenShift
- kubeconfig is stored in a secret at the end of the install

## Workflow

```
SERVICEACCOUNT=kcli
NAMESPACE=default
kubectl create serviceaccount kcli -n $NAMESPACE
kubectl create rolebinding kcli --clusterrole=admin --user=system:serviceaccount:$NAMESPACE:kcli
kubectl create secret generic pull-secret --from-file=pull-secret=openshift_pull.json
kubectl create -f kubevirt-pod.yml
```
