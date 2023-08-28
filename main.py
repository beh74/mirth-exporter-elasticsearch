"""Module to query Mirth Connect statistics and pubishing results to elasticsearch"""
import os
from datetime import datetime, timezone
import json
import logging
import requests
import xmltodict


def postprocessor(path, key, value):
    """Function to convert in int or float from json value
    Keyword arguments:
    path : json path
    key: string key
    value : int float or string value of the key
    """
    try:
        return key , int(value)
    except (ValueError, TypeError):
        try:
            return key , float(value)
        except (ValueError, TypeError):
            return key, value
    return key, value

def getdata(apiurl):
    """get api data from url. Returns a python dict
    Keyword arguments:
    apiurl : the Mirth Connect API URL
    """
    logging.debug("I query Mirth Instance ...")
    headers = {"X-Requested-With": "OpenAPI"}
    response=requests.get(os.environ['MIRTH_URL']+apiurl,
                        timeout=5,
                        auth=(os.environ['MIRTH_USER'],
                        os.environ['MIRTH_USER_PWD']),
                        headers=headers,
                        verify=False)
    if response.ok:
        data_dict = xmltodict.parse(response.content,
                                    dict_constructor=dict,
                                    postprocessor=postprocessor)
        return data_dict

    logging.error("Error pooling mirth instance - Status Code = %s", str(response.status_code))
    return None

def postelk(data):
    """Post a json data to elastic index Returns true of false
    Keyword arguments:
    data : the json payload
    """
    header = {"Content-Type": "application/json"}  
    response=requests.post(os.environ['ELK_URL'], data=data, headers=header,timeout=5)
    if response.ok:
        logging.info("Mirth statistics published to elasticsearch")
        return True

    logging.error("Error while posting data to elasticsearch - Status Code = %s",
                  str(response.status_code))
    return False

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

status=getdata('api/server/status')
logging.info("Mirth Status : %s" , str(status['int']))

stats=getdata('api/system/stats')
stats["environment"] = os.environ['MIRTH_ENV']
stats["instance"] = os.environ['MIRTH_INSTANCE_NAME']
stats["status"]= int(status['int'])
stats["@timestamp"]= datetime.now(timezone.utc).isoformat()

postelk(json.dumps(stats))
