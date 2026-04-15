# k8s

docker build -t shop-product:v1 ./product_service

docker build -t shop-order:v1 ./order_service

kubectl apply -f deploy.yaml
