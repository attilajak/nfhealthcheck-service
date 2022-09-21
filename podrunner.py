class PodRunner():

    running_pods = {}

    service_status = False


    def __init__(self,event,app):
        return self.ProcessEvent(event,app)

    def ProcessEvent(self,event,app):
        retval = False
        if event.pod_name not in self.running_pods and event.pod_applabel == app and event.isPodReady() == True:
            self.running_pods[event.pod_name] = { "app" : event.pod_applabel }
        elif event.pod_name in self.running_pods and event.pod_applabel == app and event.isPodReady() != True:
            self.running_pods.pop(event.pod_name)
        else:
            return retval
        if len(self.running_pods) >= 2:
            if not self.service_status:
                retval = True
            self.service_status = True
        else:
            if not self.service_status:
                retval = True
            self.service_status = False
        return retval
   

    def GetServiceStatus(self):
        return self.service_status
