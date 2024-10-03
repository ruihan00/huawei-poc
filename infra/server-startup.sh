cd /
git clone https://github.com/ruihan00/huawei-poc
sudo chgrp -R docker /huawei-poc
sudo chmod g+w /huawei-poc
docker run --pull always -d -p 8000:8080 -v /huawei-poc/server:/app hztiang/binacloud-huawei-poc-server

