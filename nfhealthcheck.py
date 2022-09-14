from warnings import catch_warnings
from kubernetes import config,client,watch
import sys
import os
import asyncio
import time
import signal
import json
import urllib3
import logging


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        result = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result

service_mode = "production"
#service_mode = "standalone"


pod_dictionary = {
  "podname": {
    "app" : "applabel"
  }
 
}

handler = logging.StreamHandler()
log_format = "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s"
formatter = OneLineExceptionFormatter(log_format)
handler.setFormatter(formatter)
log  = logging.getLogger()
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
log.addHandler(handler)


#config.load_incluster_config()
config.load_kube_config()



v1 = client.CoreV1Api()

def process_udrstatus(udr_status):

    log.info("Enter")

    try: 
        targetnflistfile = open("targetnflist.json", "r")
        targetnflists = json.loads(targetnflistfile.read())
        targetnflistfile.close()
        nfprofilesfile = open("nfprofiles.json", "r")
        nfprofiles = json.loads(nfprofilesfile.read())
        nfprofilesfile.close()
        nrfcaddressfile = open("config.json", "r")
        nrfcaddress = json.loads(nrfcaddressfile.read())
        service_host = nrfcaddress[service_mode][0]["url"]
        nrfcaddressfile.close()
    except:
        e = sys.exc_info()[0]
        log.info("file errors",e)

    udr_nf_instance = targetnflists["udrnflist"][0]
    udr_profile = nfprofiles[udr_nf_instance]

    udsf_nf_instance = targetnflists["udsfnflist"][0]
    udsf_profile = nfprofiles[udsf_nf_instance]
    
    http = urllib3.PoolManager()

    if udr_status == 0:
        udr_profile["nfStatus"] = "SUSPENDED"
        try:
            log.info('Connecting to:'+ 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/suspend/'+udr_nf_instance)
            con = http.request('PUT','https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/suspend/'+udr_nf_instance,body=json.dumps(udr_profile))
            log.info("Exit")
            if con.status == 200:
                log.info("Connection Success")
            else:
                log.info(con.status)
                log.info(con.headers)
        except KeyboardInterrupt:
            log.info("Keyboard Interrupt Exception")
            log.info("Exit")
        except:
            e = sys.exc_info()[0]
            log.info("Exception",e)
            log.info("Exit")
            raise RuntimeError
        

    elif udr_status == 1:
        udr_profile["nfStatus"] = "REGISTERED"
        try:
            log.info('Connecting to:'+ 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+udr_nf_instance)
            con = http.request('PUT','https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+udr_nf_instance,body=json.dumps(udr_profile))
            if con.status == 200:
                log.info("Connection Success")
            else:
                log.info(con.status)
                log.info(con.headers)
            log.info("Exit")
        except KeyboardInterrupt:
            log.info("Keyboard Interrupt Exception")
            log.info("Exit")
        except:
            e = sys.exc_info()[0]
            log.info("Connection Error %s",e)
            log.info("Exit")
            raise RuntimeError
        
        
        
def process_udsfstatus(udsf_status):
    log.info("Enter")

    targetnflistfile = open("targetnflist.json", "r")

    targetnflists = json.loads(targetnflistfile.read())

    targetnflistfile.close()

    nfprofilesfile = open("nfprofiles.json", "r")

    nfprofiles = json.loads(nfprofilesfile.read())

    nfprofilesfile.close()

    nrfcaddressfile = open("config.json", "r")
    nrfcaddress = json.loads(nrfcaddressfile.read())
    service_host = nrfcaddress[service_mode][0]["url"]

    nrfcaddressfile.close()

    udr_nf_instance = targetnflists["udrnflist"][0]
    udr_profile = nfprofiles[udr_nf_instance]

    udsf_nf_instance = targetnflists["udsfnflist"][0]
    udsf_profile = nfprofiles[udsf_nf_instance]
    
    http = urllib3.PoolManager()
   

    if udsf_status == 0:
        # read config and send SUSPENDED to NRFC
        udsf_profile["nfStatus"] = "SUSPENDED"
        try:
            log.info('Connecting to:'+ 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+udsf_nf_instance)
            con = http.request('PUT','https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/suspend/'+udsf_nf_instance,body=json.dumps(udsf_profile))
            if con.status == 200:
                log.info("Connection Success")
            else:
                log.info(con.status)
                log.info(con.headers)
            log.info("Exit")
        except KeyboardInterrupt:
            log.info("Connection Error - Keyboard Interrupt ")
            log.info("Exit")
        except:
            e = sys.exc_info()[0]
            log.info("Connection Error %s",e)
            log.info("Exit")
            raise RuntimeError
        
    elif udsf_status == 1:
        # read config and send REGISTERED to NRFC
        udsf_profile["nfStatus"] = "REGISTERED"
        try:
            log.info('Connecting to:'+ 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+udsf_nf_instance)
            con = http.request('PUT','https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+udsf_nf_instance,body=json.dumps(udsf_profile))
            if con.status == 200:
                log.info("Connection Success")
            else:
                log.info(con.status)
                log.info(con.headers)
            log.info("Exit")
        except KeyboardInterrupt:
            log.info("Connection Error - Keyboard Interrupt ")
            log.info("Exit")
        except:
            e = sys.exc_info()[0]
            log.info("Connection Error %s",e)
            log.info("Exit")
            raise RuntimeError





async def pods():

    udr_running_count = 0
    udsf_running_count = 0
    nrfc_running = 0

    udr_status = 0
    udsf_status = 0

    log.info("Enter")
    w = watch.Watch()

    log.info("Watch Invoked")
    try:
            
        for event in w.stream(v1.list_namespaced_pod,namespace="default",label_selector='app in (udr, udsf, nrfc)',watch=False):
            log.info("Event Arrived")
            log.info("Event: %s %s %s %s %s" % (event['type'], event['object'].kind, event['object'].metadata.name, event['object'].status.phase,event['object'].metadata.labels))
            if event['object'].metadata.name not in pod_dictionary and  event['object'].metadata.labels["app"] == "nrfc" and event['object'].status.phase == "Running":
                pod_dictionary[event['object'].metadata.name] = { "app" : event['object'].metadata.labels["app"] }
                log.info("nrfc is running")
                nrfc_running = 1
            elif event['object'].metadata.labels["app"] == "nrfc" and event['object'].status.phase != "Running":
                log.info("nrfc is not ready")
                if event['object'].metadata.name in pod_dictionary:
                    pod_dictionary.pop(event['object'].metadata.name)
                    nrfc_running = 0
            #check for number of running udr pods
            if event['object'].metadata.name not in pod_dictionary and event['object'].metadata.labels["app"] == "udr" and event['object'].status.phase == "Running":
                pod_dictionary[event['object'].metadata.name] = { "app" : event['object'].metadata.labels["app"] }
                udr_running_count += 1
            if event['object'].metadata.name not in pod_dictionary and event['object'].metadata.labels["app"] == "udsf" and event['object'].status.phase == "Running":
                pod_dictionary[event['object'].metadata.name] = { "app" : event['object'].metadata.labels["app"] }
                udsf_running_count += 1
            if event['type'] == "DELETED" and event['object'].metadata.labels["app"] == "udr":
                if event['object'].metadata.name in pod_dictionary:
                    pod_dictionary.pop(event['object'].metadata.name)
                udr_running_count -= 1
            if event['type'] == "DELETED" and event['object'].metadata.labels["app"] == "udsf":
                if event['object'].metadata.name in pod_dictionary:
                    pod_dictionary.pop(event['object'].metadata.name)
                udsf_running_count -= 1
            if event['type'] == "DELETED" and event['object'].metadata.labels["app"] == "nrfc":
                if event['object'].metadata.name in pod_dictionary:
                    pod_dictionary.pop(event['object'].metadata.name)
                    nrfc_running = 0

            log.info("udr_running_count: %s, udsf_running_count: %s" % (udr_running_count,udsf_running_count))

            if udr_status == 0 and udr_running_count >= 2:
                if nrfc_running == 1:
                    udr_status = 1
                    try:
                        process_udrstatus(udr_status)
                    except ( RuntimeError) as e:
                        log.info("process_udrstatus error %s",e)
            elif udr_status == 1 and udr_running_count < 2:
                  if nrfc_running == 1:
                      udr_status = 0
                      try:
                          process_udrstatus(udr_status)
                      except ( RuntimeError) as e:
                          log.info("process_udrstatus error %s",e)
            
            if udsf_status == 0 and udsf_running_count >= 2:
                if nrfc_running == 1:
                    udsf_status = 1
                    try:
                        process_udsfstatus(udsf_status)
                    except ( RuntimeError) as e:
                        log.info("process_udsfstatus error %s",e)
            elif udsf_status == 1 and udsf_running_count < 2:
                  if nrfc_running == 1:
                      udsf_status = 0
                      try:
                          process_udsfstatus(udsf_status)
                      except ( RuntimeError) as e:
                          log.info("process_udsfstatus error %s",e)
            
            log.info("udr_status: %s, udsf_status: %s" % (udr_status,udsf_status))
            await asyncio.sleep(0)

    except KeyboardInterrupt:
                log.info("Key Board Interrupt")
                exit()
    except:
                e = sys.exc_info()[0]
                log.info("Exception Occured:",e)
