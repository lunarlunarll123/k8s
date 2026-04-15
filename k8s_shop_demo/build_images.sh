#!/bin/bash
echo "🐳 Building Docker Images locally..."

# Build Product Service Image
docker build -t shop-product:v1 ./product_service

# Build Order Service Image
docker build -t shop-order:v1 ./order_service

echo "✅ Images built: shop-product:v1, shop-order:v1"
echo "👉 Now run: kubectl apply -f deploy.yaml"
