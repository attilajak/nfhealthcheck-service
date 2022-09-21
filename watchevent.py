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
    pod_event = None


    def __init__(self, event):
        self.ProcessEvent(event)

    
    def ProcessEvent(self,event):

        self.pod_eventtype = event['type']
        self.pod_name = event['object'].metadata.name
        self.pod_applabel = event['object'].metadata.labels["app"]
        self.pod_event = event



    def isPodReady(self):
        status = self.pod_event['object'].status
        for condition in status.conditions:
            if condition.type == "Ready" and condition.status == "True":
                self.pod_status = True
                return self.pod_status
        return False

    
