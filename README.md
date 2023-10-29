# felfel
flask app

## Steps

Instruction was prepared for Ubuntu 22.04

### 1

```
sudo apt install python3-pip
pip install flask redis
pip freeze -l > requirements.txt
```

`python3 app.py`

### 2

```
sudo apt install docker.io
docker build -t felfel-app:latest .
docker run -d -p 8080:8080 --rm --name felfel-app felfel-app:latest
docker run -d -p 8080:8080 --rm --name felfel-app -e REDIS_USERNAME=user -e REDIS_PASSWORD=pass -e REDIS_HOST=felfel-redis -e REDIS_PORT=6379 -e REDIS_DB=0 felfel-app:latest
```

### 3

```
sudo apt install docker-compose
```

```
REDIS_USERNAME=user REDIS_PASSWORD=pass REDIS_HOST=felfel-redis REDIS_PORT=6379 REDIS_DB=0 docker-compose up
```
or use dotenv to hide credentials

### 4

```
pip install prometheus_client
pip freeze -l > requirements.txt
```

```
REDIS_USERNAME=user REDIS_PASSWORD=pass REDIS_HOST=felfel-redis REDIS_PORT=6379 REDIS_DB=0 docker-compose up --build
```
or use dotenv to hide credentials

### 5

```
docker tag felfel:latest toleksa/felfel-app:latest
docker login
docker push toleksa/felfel-app:latest
```

Minikube:
```
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb --output-dir "/tmp"
sudo dpkg -i /tmp/minikube_latest_amd64.deb
minikube start
minikube addons enable ingress
curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sudo bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install --create-namespace --namespace monitoring prometheus prometheus-community/kube-prometheus-stack
kubectl apply -f kube.yaml
```

Rancher - RKE2:
```
curl -sfL https://get.rke2.io | sudo sh -
systemctl enable rke2-server.service
systemctl start rke2-server.service
echo "export PATH=\$PATH:/var/lib/rancher/rke2/bin" >> ~/.bashrc
echo "export KUBECONFIG=/etc/rancher/rke2/rke2.yaml" >> ~/.bashrc
echo "alias k='kubectl'" >> ~/.bashrc
. ~/.bashrc
while ! `kubectl -n kube-system get ValidatingWebhookConfiguration rke2-ingress-nginx-admission &>> /dev/null` ; do echo -n . ; sleep 1s ; done
kubectl delete -A ValidatingWebhookConfiguration rke2-ingress-nginx-admission
kubectl apply -f - <<EOF
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: rke2-ingress-nginx
  namespace: kube-system
spec:
  valuesContent: |-
    controller:
      publishService:
        enabled: true
        pathOverride: kube-system/rke2-ingress-nginx-controller
      service:
        enabled: true
        type: LoadBalancer
EOF
curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | sudo bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install --create-namespace --namespace monitoring prometheus prometheus-community/kube-prometheus-stack
helm install --create-namespace --namespace metallb-system metallb bitnami/metallb
kubectl -n metallb-system rollout status deployment metallb-controller
kubectl -n metallb-system apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: metallb-pool-default
  namespace: metallb-system
spec:
  addresses:
  - `hostname -I | awk '{print $1"/32"}'`
EOF
kubectl apply -f kube.yaml
```
