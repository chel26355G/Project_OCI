### 1. service.yaml 로 파드 생성
 kubectl run nginx-for-service --image=nginx --replicas=2 --port=80 --labels="app=nginx-for-svc"
### 2. loadblancer 타입 서비스 사용
 kubectl apply -f loadbalancer.yaml
### 3. 생성 확인 -> external IP 할당
 kubectl get svc
