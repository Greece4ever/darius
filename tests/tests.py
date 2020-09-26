from ..server.server import WebsocketServer,HttpServer,RoutedWebsocketServer,Server
from ..server.routes import View,template,SocketView
from ..client_side import status
# from cache import Cache
import pprint
import os

# cache = Cache("cache.sqlite3","Cache",(1,datetime.timedelta(seconds=10)))

class Home(View):

    # @cache.CacheDecorator
    def GET(self,request,**kwargs):
        isperm = kwargs.get('isPermitted')
        if isperm:
            return status.Http200().__call__("Home Page") 
        return status.Http429().__call__("Too many requests 429")

class ShitJson(View):
    def GET(self,request):
        return status.HttpJson().__call__({"hello" : 1},200)

class Chat(View):
    def GET(self,request):
        return status.Http200().__call__(template(os.path.join(os.getcwd(),"index.html")))

class Chat2(View):
    def GET(self,request):
        return status.Http200().__call__(template(os.path.join(os.getcwd(),"test.html"),usePythonScript=True))

class RView(View):
    def GET(self,request):
        context = {
            'words' :["a",
                    "abandon",
                    "ability",
                    "able",
                    "abortion",
                    "about",
                    "above",
                    "abroad",
                    "absence",
                    "absolute",
                    "absolutely",
                    "absorb"]
        }
        # page_num = request['method'].split('/')[-1]
        # return status.Http200().__call__("<h2>You've visited page number {}!</h2>".format(page_num))
        return status.Http200().__call__(template("test.html",usePythonScript=True,context=context))

import os

class Imgres(View):
    def GET(self,request):
        return status.HttpBinary().__call__(os.path.join(r'C:\Users\Spartakos\Desktop','ΑΣΘΕΝΙΔΗΣ ΛΕΩΝΙΔΑΣ.PDF'),200,display_in_browser=True)

class SampleView(View):
    def GET(self,request):
        from random import random
        context = {
            'random' : [
                [int(random() * 255) for _ in range(3)] for __ in range(10) ]
        }
        return status.Http200().__call__(template(r"C:\Users\Spartakos\Desktop\server\tests\test.html",usePythonScript=True,context=context))

    def POST(self,request):
        pprint.pprint(request)
        return status.Http200().__call__("<h1>Helo World!</h1>")

class PostView(View):
    def GET(self, request):
        return status.Http200().__call__(template(r"C:\Users\Spartakos\Desktop\server\tests\test.html",usePythonScript=True))

    def POST(self,request):
        # if len(request[-1]) > 0:
        #     DIR_NAME : str = POST_DATA
        #     os.mkdir(DIR_NAME)
        #     for item in request[0]:
        #         with open(os.path.join(os.getcwd(),DIR_NAME,item[]),'wb+') as f:
        #             f.write(item['data'])
        pprint.pprint(request)
        return status.Http200().__call__("""<span style='color : red' >if</span><span>(<span>x</span>==<span style='color : blue'>1</span>)""")

class RedirectView(View):
    def GET(self,request):
        return status.Redirect().__call__('/poutsa')

URLS : dict = {
    r"^(\/)?" : Home(),
    '/another' : ShitJson(),
    '/chat' : Chat(),
    '/chat2' : Chat2(),
    r'(\/)images\/(\d+)(\/)?' : Imgres(),
    r'\/profiles\/(\w+)(\/)?' : RView(),
    r'(\/)tests(\/)(\d+)(\/)?' : SampleView(),
    r'/post' : PostView(),
    r'/redirect' : RedirectView()
}

class CustomRoute(SocketView):
    def onConnect(self,client,**kwargs):
        #Get the **kwarg arguments
        key = kwargs.get("key")
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        msg_to_send = "{} has connected!".format(self.get_client_ip(client))

        #Accept the user send send him the message
        self.accept(client=client,key=key) #Accept the client request
        send(client,msg_to_send)


        #Send the message to all the clients in the same path that someone has connected
        for client in path_info['clients']:
            send(client,msg_to_send)
        return True

    def onMessage(self,**kwargs):
        """Gets called when a message is received from the client side"""
        data = kwargs.get('data')
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        for client in path_info['clients']:
            send(client,data)

    def onExit(self,client,**kwargs):
        path_info = kwargs.get("path_info")
        send = kwargs.get('send_function')
        for client in path_info['clients']:
            send(client,"{} has left!".format(self.get_client_ip(client)))

class ChatRoute(CustomRoute):
    pass

PATHS = {
    '/peos' : CustomRoute(),
    '/chat' : ChatRoute()
}

URLS['/SQL'] = CustomRoute()

server = HttpServer(URLS=URLS,port=8000)
# server = Server(PATHS,URLS,port=80)
server.start()