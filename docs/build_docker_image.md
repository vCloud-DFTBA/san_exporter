# Build and deploy SAN exporter

**Build new image**

```
git pull origin master

docker build -t registry/san-exporter:latest .
docker push registry/san-exporter:latest
```

**Run new container**

```
// create san-exporter volume for the first deploy

docker volume create san-exporter
mkdir /root/san-exporter

// config
vim /root/san-exporter/config.yml

docker pull registry/san-exporter:latest

docker run -d -p 8888:8888 -v san-exporter:/var/log/ -v /root/san-exporter/config.yml:/san-exporter/config.yml --name san-exporter registry/san-exporter:latest
```
