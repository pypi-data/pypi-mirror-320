

class DFAgent:
    def __init__(self,system_host):
        self.host = system_host
        
        self.server_list = {
            #'outbound': '127.0.0.1:11402',
            #'transport': '127.0.0.1:11301'
        }
    def registerForDfService(self,dfserver_name_list,dfserver_port):
        for i in range(len(dfserver_name_list)):
            self.server_list[dfserver_name_list[i]] = self.host+":"+str(dfserver_port)
    def logOutOfDfService(self,dfserver_name):
        del self.server_list[dfserver_name]
    def SearchDFAgent(self,dfserver_name):
        if dfserver_name in self.server_list.keys():
            return self.server_list[dfserver_name]
        else:
            return []