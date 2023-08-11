import requests
import xmltodict
import logging
from logging.handlers import RotatingFileHandler
import os
import json
from datetime import datetime, timezone

def postprocessor(path, key, value):
    try:
        return key , int(value)
    except (ValueError, TypeError):
        try:
            return key , float(value)
        except (ValueError, TypeError):
            return key, value
    return key, value

def getdata(apiurl):
    logging.debug("I query Mirth Instance ...")
    headers = {"X-Requested-With": "OpenAPI"}
    response=requests.get(os.environ['MIRTH_URL']+apiurl, timeout=5, auth=(os.environ['MIRTH_USER'], os.environ['MIRTH_USER_PWD']),headers=headers, verify=False)
    if (response.ok):
        data_dict = xmltodict.parse(response.content, dict_constructor=dict, postprocessor=postprocessor)
        return data_dict
    else:
        logging.error("Error pooling mirth instance - Status Code ="+ str(response.status_code))
        return None

def postelk(data):
    header = {"Content-Type": "application/json"}  
    response=requests.post(os.environ['ELK_URL'], data=data, headers=header)
    if (response.ok):
        logging.info("Mirth statistics published to elasticsearch")
        return True
    else:
        logging.error("Error while posting data to elasticsearch - Status Code ="+ str(response.status_code))
        return False

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

status=getdata('api/server/status')
logging.info("Mirth Status : " + str(status['int']))

stats=getdata('api/system/stats')
stats["environment"] = os.environ['MIRTH_ENV']
stats["instance"] = os.environ['MIRTH_INSTANCE_NAME']
stats["status"]= int(status['int'])
stats["@timestamp"]= datetime.now(timezone.utc).isoformat()

postelk(json.dumps( stats))