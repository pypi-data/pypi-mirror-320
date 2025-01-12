import threading
import yaml
from MultiAgentKit.utilities.TCPClient import TCPClient
from MultiAgentKit.utilities.tool import print_error
from Protocols.common import Protocol_Common

class Agent:
    def __init__(self,ymal_file):
        with open(ymal_file, 'r',encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.__dict__.update(self.config)
        self.connectDevice()
        self.protocol_common = Protocol_Common()
        
    
    def connectDevice(self):
        """连接设备"""
        self.device_connetction =  TCPClient(self.device['ip'],self.device['port'])
        if self.device_connetction.connect():
            print("Agent {}连接设备成功!".format(self.agent_name))
        else:
            print_error("连接设备失败!")

    def startBehaviours(self, target_method):
        """封装线程启动和等待的方法"""
        thread = threading.Thread(target=target_method.run)
        thread.start()
        #thread.join()
    
    def __exit__(self):
        self.device_connetction.close()


if __name__ == '__main__':
    agent = Agent()