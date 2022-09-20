import sys
import os
from warnings import catch_warnings
from kubernetes import config,client,watch

class WatchEvent() :

    pod_status = False
    pod_name = ""
    pod_applabel = ""
    pod_eventtype = ""
    pod_status = None


    def __init__(self, event):
        self.ProcessEvent(event)

    
    def ProcessEvent(event):

        pod_status = event['object'].status
        pod_eventtype = event['type']
        pod_name = event['object'].metadata.name
        pod_applabel = event['object'].metadata.labels["app"]

        for condition in pod_status["conditions"]:
            if condition["type"] == "Ready" and condition["status"] == "True":
                pod_status = True


    def isPodReady(self):
        return self.pod_status

    