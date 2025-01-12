

class DFAgent:
    def __init__(self):
        self.server_list = {
            'outbound': '127.0.0.1:11402',
            'transport': '127.0.0.1:11301'
        }
    def SearchDFAgent(self,dfserver_name):
        if dfserver_name in self.server_list.keys():
            return self.server_list[dfserver_name]
        else:
            return []