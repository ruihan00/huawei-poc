# Install Nvidia drivers
sudo /opt/deeplearning/install-driver.sh

# Clone server code
cd /
git clone https://github.com/ruihan00/huawei-poc

# Fix permissions issue
sudo chgrp -R docker /huawei-poc
sudo chmod g+w /huawei-poc

# Start docker
docker run                   \
    --pull always            \
    -d                       \
    -p 8000:8080             \
    --gpus all               \
    --restart unless-stopped \
    -v /huawei-poc/server:/app hztiang/binacloud-huawei-poc-server


