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
from podrunner import PodRunner
from watchevent import WatchEvent


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

udr_runner = PodRunner("udr")
udsf_runner = PodRunner("udsf")

pod_dictionary = {}

handler = logging.StreamHandler()
log_format = "%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s] %(message)s"
formatter = OneLineExceptionFormatter(log_format)
handler.setFormatter(formatter)
log  = logging.getLogger()
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))
log.addHandler(handler)


config.load_incluster_config()
#config.load_kube_config()



v1 = client.CoreV1Api()

def process_servicestatus(status,app):

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

    if app == "udr":
        nf_instance = targetnflists["udrnflist"][0]
        profile = nfprofiles[nf_instance]
    elif app == "udsf":
        nf_instance = targetnflists["udsfnflist"][0]
        profile = nfprofiles[nf_instance]
    
    http = urllib3.PoolManager()

    if not status:
        profile["nfStatus"] = "SUSPENDED"
        url = 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/suspend/'+nf_instance
    elif status:
        profile["nfStatus"] = "REGISTERED"
        url = 'https://'+service_host+":"+ str(nrfcaddress[service_mode][0]["port"])+'/nrfclient/register/'+nf_instance

    try:
        log.info('Connecting to:'+ url)
        con = http.request('PUT',url,body=json.dumps(profile))
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
        
        
async def pods():

    nrfc_running = 0

    udr_statuschange = False
    udsf_statuschange = False

    log.info("Enter")
    w = watch.Watch()

    log.info("Watch Invoked")
    try:
            
        for event in w.stream(v1.list_namespaced_pod,namespace="default",label_selector='app in (udr, udsf, nrfc)',watch=False):
            log.info("Event Arrived")
             
            watchevent = WatchEvent()

            watchevent.process_event(event)

            log.info("Event: %s %s %s" % (watchevent.pod_eventtype, watchevent.pod_name, event['object'].status.conditions))


            if watchevent.pod_name not in pod_dictionary and  watchevent.pod_applabel == "nrfc" and watchevent.is_pod_ready() == True:
                pod_dictionary[watchevent.pod_name] = { "app" : watchevent.pod_applabel }
                log.info("nrfc is running")
                nrfc_running = 1
            elif watchevent.pod_applabel == "nrfc" and watchevent.is_pod_ready() != True:
                log.info("nrfc is not ready")
                if watchevent.pod_name in pod_dictionary:
                    pod_dictionary.pop(watchevent.pod_name)
                    nrfc_running = 0

            if watchevent.pod_applabel == "udr":
                udr_statuschange = udr_runner.process_event(watchevent)
                log.info("udr_statuschange: " + str(udr_statuschange))

            if watchevent.pod_applabel == "udsf":
                udsf_statuschange = udsf_runner.process_event(watchevent)
                log.info("udsf_statuschange: " + str(udsf_statuschange))

            
            if watchevent.is_pod_ready() == False and watchevent.pod_applabel == "nrfc":
                if watchevent.pod_name in pod_dictionary:
                    pod_dictionary.pop(watchevent.pod_name)
                    nrfc_running = 0
            
            if nrfc_running == 1 and udr_statuschange: 
                try: 
                    process_servicestatus(udr_runner.get_service_status(),"udr") 
                    udr_statuschange = False
                except ( RuntimeError) as e:
                    udr_statuschange = False
                    log.info("process_servicestatus error %s",e)
            if nrfc_running == 1 and udsf_statuschange: 
                try: 
                    process_servicestatus(udsf_runner.get_service_status(),"udsf") 
                    udsf_statuschange = False
                except ( RuntimeError) as e:
                    udsf_statuschange = False
                    log.info("process_servicestatus error %s",e)
            
            await asyncio.sleep(0)

    except KeyboardInterrupt:
                log.info("Key Board Interrupt")
                exit()
    except:
                e = sys.exc_info()[0]
                log.info("Exception Occured:",e)
