import socket
from typing import Union
import status
from datetime import datetime
import re
import threading
import base64 
from communications import SocketBin,SocketBinSend

LOCALHOST : str = "127.0.0.1"
HTTP_PORT : int = 80

class Server:
    def __init__(self,host : str = LOCALHOST,port : int = HTTP_PORT,http : bool = True):
        print(f"Starting local {'HTTP' if http else 'WS'} Server on {host}:{port}")
        self.adress = (host,port)
        self.connection = socket.socket()
        self.connection.bind(self.adress)
    
    def ParseHeaders(self,request : Union[bytes,str]):
            HEADERS = {}
            XS = request.decode('utf-8').split("\r\n")
            XS = [item for item in XS if item.strip() != '']
            HEADERS['method'] = XS.pop(0).replace("HTTP/1.1",'').strip()
            term : str
            for term in XS:
                spl : list = term.split(":")
                HEADERS[spl[0].strip()] = spl[1].strip()
            return HEADERS

    def AwaitRequest(self,URLS : dict):
        while True:
            self.connection.listen(1)
            address : tuple
            client,address = self.connection.accept()
            request = client.recv(1024)
            if len(request) == 0:
                break
            headers = self.ParseHeaders(request)
            print(f'(HTTP) : {headers["method"]} | {str(datetime.now())} : {address}')
            URL = headers["method"]
            target = URL.split(" ")[1]
            if not target in URLS:
                client.send(status.Http404.__call__("<b>Page {} Was not Found (404 Status Code)</b>".format(target)))
            else:
                try:
                    client.send(URLS.get(target).__call__(headers))
                except Exception as error:
                    print(f'[ERROR] : {error}')
                    client.send(status.Http500().__call__("<h1>Internal Server Error</h1>"))

            client.close()

class WebsocketServer(Server):
    def __init__(self,host : str = LOCALHOST,port : int = 8000):
        self.clients : list = [] #Store all the clients
        super(WebsocketServer,self).__init__(host=host,port=port,http=False)

    def AwaitSocket(self):
        self.connection.listen(1)
        while True:
            client,adress = self.connection.accept()
            t = threading.Thread(target=self.AwaitMessage,args=(client,adress))
            t.start()

    def onMessage(self,**kwargs):
        s_function = kwargs.get('s_function')
        data = kwargs.get('data')
        for client in self.clients:
            s_function(data)

    def send(self,client,data : bytes) -> None:
        client.send(SocketBinSend(data))

    def AwaitMessage(self,client,address):
        while True:
            data = client.recv(1024)
            if len(data) == 0:
                if client in self.clients:
                    indx = self.clients.index(client)
                    self.clients.pop(indx)
                break
            try: #Headers Can Be Parsed, New connection
                headers = self.ParseHeaders(data)
                self.clients.append(client)
                HTTP_MSG = status.Http101().__call__("da",headers['Sec-WebSocket-Key'])
                client.send(HTTP_MSG)
                print(f"(WS) : {str(datetime.now())} Connection Established {address}")
            except: #Out of range error, client send a bytes object
                print(f"(WS) : {str(datetime.now())} Received Message {address}")
                decoded = SocketBin(data)
                self.onMessage(data=decoded,s_function=self.send,sender_client=client)
                    
                    # base64.b64decode(data)
                    # client.send("Hello".encode())
        client.close()

