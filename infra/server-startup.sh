# Install Nvidia drivers
sudo /opt/deeplearning/install-driver.sh

# Clone server code
cd /
git clone https://github.com/ruihan00/huawei-poc

# Fix permissions issue
sudo chgrp -R docker /huawei-poc
sudo chmod g+w /huawei-poc

# Start docker
docker compose -f docker-compose.prod.yml up -d
