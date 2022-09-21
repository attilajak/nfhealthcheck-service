"""A dummy docstring."""
class PodRunner():
    """A dummy docstring."""

    running_pods = None

    service_status = None

    app = None

    def __init__(self,app): 
        """A dummy docstring."""
        self.app = app
        self.running_pods = {}
        self.service_status = False

    def process_event(self,event):
        """A dummy docstring."""
        retval = False
        if event.pod_name not in self.running_pods and  event.is_pod_ready():
            self.running_pods[event.pod_name] = {"app" : event.pod_applabel}
        elif event.pod_name in self.running_pods and not event.is_pod_ready():
            self.running_pods.pop(event.pod_name)
        else:
            print("return with no luck")
            return retval

        print("length of " + self.app +" running pods:", len(self.running_pods))
        print("service_status : ", self.service_status)

        if len(self.running_pods) >= 2 and not self.service_status:
            retval = True
            self.service_status = True
        elif len(self.running_pods) < 2 and self.service_status:
            retval = True
            self.service_status = False
        return retval

    def get_service_status(self):
        """A dummy docstring."""
        return self.service_status
