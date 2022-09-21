import sys
import os
from warnings import catch_warnings
from kubernetes import config,client,watch

class WatchEvent() :

    pod_status = None
    pod_name = ""
    pod_applabel = ""
    pod_eventtype = ""
    pod_event = None


    def __init__(self):
        self.pod_status = False

    
    def process_event(self,event):

        self.pod_eventtype = event['type']
        self.pod_name = event['object'].metadata.name
        self.pod_applabel = event['object'].metadata.labels["app"]
        self.pod_event = event



    def is_pod_ready(self):
        status = self.pod_event['object'].status
        if status.conditions != None: 
            for condition in status.conditions:
                if condition.type == "Ready" and condition.status == "True": 
                    self.pod_status = True 
                    return self.pod_status
        return False
