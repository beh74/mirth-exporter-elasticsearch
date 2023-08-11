# mirth-exporter-elasticsearch
A Nextgen healthcare Mirth exporter - Exporting Mirth statistics on JVM, CPU and disk utilization
Mirth version should be >= 3.9

## How to use it

```
docker run -e ELK_URL="https://elastic:mypassword@emyelasticserver/docker-mirth/_doc" \
 -e MIRTH_ENV="PROD" \
 -e MIRTH_INSTANCE_NAME="mirth-xx" \
 -e MIRTH_URL="https://mymirthserver:9443/" \
 -e MIRTH_USER="admin"\ 
 -e MIRTH_USER_PWD="mymirthpassword" \
 -e PYTHONWARNINGS="ignore:Unverified HTTPS request" hug-mirth-stats-exporter:latest
 ```

## How does it works

The container is using a crontab to run a statistics pull every 5 minutes (see crontab.file) with Mirth api : api/system/stats

## Use kibana to display statistics

![Alt text](images/kibana.png?raw=true "Kibana dashboard sample")
