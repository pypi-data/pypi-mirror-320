# https://buymeacoffee.com/apintio

import re
import struct
import random
import socket
import threading
import websockets
import asyncio
import time
import ntplib

####### IID ###


default_ntp_server = "be.pool.ntp.org"
default_global_ntp_offset_in_milliseconds = 0


def get_default_global_ntp_offset_in_milliseconds():
    return default_global_ntp_offset_in_milliseconds

    
def bytes_to_int(bytes:bytes):
    value= struct.unpack('<i', bytes)[0]
    return value

def bytes_to_index_integer(bytes:bytes):
    index, value = struct.unpack('<ii', bytes)
    return index, value

def  bytes_to_index_integer_date(bytes:bytes):
    index, value, date = struct.unpack('<iiQ', bytes)
    return index, value, date



def integer_to_bytes(value:int):
    return struct.pack('<i', value)

def index_integer_to_bytes(index:int, value:int):
    return struct.pack('<ii', index, value)

def index_integer_date_to_bytes(index:int, value:int, date:int):
    return struct.pack('<iiQ', index, value, int(date))

def index_integer_date_to_bytes(index:int, value:int, date:int):
    return struct.pack('<iiQ', index, value, int(date))

def index_integer_now_relay_milliseconds_to_bytes(index: int, value: int, delay_in_milliseconds: int) -> bytes:
    current_time_milliseconds = int(time.time() * 1000)
    adjusted_time_milliseconds = current_time_milliseconds + delay_in_milliseconds + default_global_ntp_offset_in_milliseconds
    return struct.pack('<iiQ', index, value, int(adjusted_time_milliseconds))


def text_shortcut_to_bytes(text:str):
    try:
        if text.startswith("i:"):
            integer = int(text.split(":")[1])
            return integer_to_bytes(integer)
        elif text.startswith("ii:"):
            index, integer = text.split(":")[1].split(",")
            return index_integer_to_bytes(int(index), int(integer))
        elif text.startswith("iid:"):
            index, integer, delay = text.split(":")[1].split(",")
            
            return index_integer_now_relay_milliseconds_to_bytes(int(index), int(integer), int(delay))
        else:
            while "  " in text:
                text = text.replace("  ", " ")
            tokens : list = text.replace(",", " ").split(" ")
            size = len(tokens)
            if size == 1:
                integer = int(text)
                return integer_to_bytes(integer)
            elif size == 2:
                index = int(tokens[0])
                integer = int(tokens[1])
                return index_integer_to_bytes(index, integer)
            elif size == 3:
                index = int(tokens[0])
                integer = int(tokens[1])
                delay = int(tokens[2])
                return index_integer_now_relay_milliseconds_to_bytes(index, integer, delay)
            else:
                integer = int(text)
                return integer_to_bytes(integer)
    except Exception as e:
        print("Error", e)    
    return None
        
def get_random_integer(from_value:int, to_value:int):
    return random.randint(from_value, to_value)
def get_random_integer_100():
    return get_random_integer(0, 100)
def get_random_integer_int_max():
    return get_random_integer(-2147483647, 2147483647)

def get_random_integer_int_max_positive():
    return get_random_integer(0, 2147483647)
        
def i(integer_value:int):
    return integer_to_bytes(integer_value)

def ii(index:int, integer_value:int):
    return index_integer_to_bytes(index, integer_value)

def iid(index:int, integer_value:int, date:int):
    return index_integer_date_to_bytes(index, integer_value, date)

def iid_ms(index:int, integer_value:int, milliseconds:int):
    return index_integer_date_to_bytes(index, integer_value, milliseconds)
   
   
   
def is_text_ivp4(server_name:str):
    # check if the string is in 255.255.255.255 format
    pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return bool(pattern.match(server_name))

def get_ipv4(server_name:str):
    if is_text_ivp4(server_name):
        return server_name
    ivp4 = socket.gethostbyname(server_name)
    return ivp4



class NtpOffsetFetcher:
    
    def fetch_ntp_offset_in_milliseconds( ntp_server):
        try:
            c = ntplib.NTPClient()
            response = c.request(ntp_server)
            return response.offset*1000
        except Exception as e:
            print(f"Error NTP Fetch: {ntp_server}", e)
            return 0


def set_global_ntp_offset_in_milliseconds(ntp_server=default_ntp_server):

    try:
        offset=  NtpOffsetFetcher.fetch_ntp_offset_in_milliseconds(ntp_server)
        global default_global_ntp_offset_in_milliseconds
        default_global_ntp_offset_in_milliseconds = offset
        print (f"Default Global NTP Offset: {default_global_ntp_offset_in_milliseconds} {ntp_server}" )
    except Exception as e:
        pass
        default_global_ntp_offset_in_milliseconds = 0
set_global_ntp_offset_in_milliseconds()
    
## UDP IID
### SEND UDP IID
class SendUdpIID:
    
    def __init__(self, ivp4, port, use_ntp:bool):
        
        self.ivp4 = get_ipv4(ivp4)
        self.port = port
        self.ntp_offset_local_to_server_in_milliseconds=0
        
        if use_ntp:
            self.fetch_ntp_offset()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def get_ntp_offset(self):
        return self.ntp_offset_local_to_server_in_milliseconds
        
    def push_integer_as_shorcut(self, text:str):
        bytes = text_shortcut_to_bytes(text)
        if bytes:
            self.sock.sendto(bytes, (self.ivp4, self.port))
    def push_bytes(self, bytes:bytes):
        self.sock.sendto(bytes, (self.ivp4, self.port))
        
    def push_text(self, text:str):
        self.push_bytes(text.encode('utf-8'))
        
    def push_integer(self, value:int):
        self.push_bytes(integer_to_bytes(value))
        
    def push_index_integer(self, index:int, value:int):
        self.push_bytes(index_integer_to_bytes(index, value))
        
    def push_index_integer_date(self, index:int, value:int, date:int):
        self.push_bytes(index_integer_date_to_bytes(index, value, date))
        
    def push_random_integer(self, index:int, from_value:int, to_value:int):
        value = random.randint(from_value, to_value)
        self.push_index_integer(index, value)
        
    def push_random_integer_100(self, index:int):
        self.push_random_integer(index, 0, 100)
        
    def push_random_integer_int_max(self, index:int):
        self.push_random_integer(index, -2147483647, 2147483647)
        
    def fetch_ntp_offset(self, ntp_server="be.pool.ntp.org"):        
        self.set_ntp_offset_tick(NtpOffsetFetcher.fetch_ntp_offset_in_milliseconds(ntp_server))
        print (f"NTP Offset: {self.ntp_offset_local_to_server_in_milliseconds}")

    def set_ntp_offset_tick(self, ntp_offset_local_to_server:int):
        self.ntp_offset_local_to_server_in_milliseconds=ntp_offset_local_to_server
    
    def push_index_integer_date_local_now(self, index:int, value:int):
        date = int(time.time())
        self.push_index_integer_date(index, value, date)
        
    def push_index_integer_date_ntp_now(self, index:int, value:int):
        date = int(time.time()) + self.ntp_offset_local_to_server_in_milliseconds
        self.push_index_integer_date(index, value, date)
   
    def push_index_integer_date_ntp_in_milliseconds(self, index:int, value:int, milliseconds:int):
        date = int(time.time()) + self.ntp_offset_local_to_server_in_milliseconds + milliseconds/1000
        self.push_index_integer_date(index, value, date)
        
   
    def push_index_integer_date_ntp_in_seconds(self, index:int, value:int, seconds:int):
        self.push_index_integer_date_ntp_in_milliseconds(index, value, seconds*1000)



## UDP IID
### RECEIVE UDP IID
class ListenUdpIID:
    def __init__(self, ivp4, port):
        self.ivp4 = get_ipv4(ivp4)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ivp4, self.port))
        self.on_receive_integer = None
        self.on_receive_index_integer = None
        self.on_receive_index_integer_date = None
        # Start thread
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        
    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data is None:
                    continue
                size = len(data)
                if size == 4:
                    value = bytes_to_int(data)
                    if self.on_receive_integer:
                        self.on_receive_integer(value)
                elif size == 8:
                    index, value = bytes_to_index_integer(data)
                    if self.on_receive_index_integer:
                        self.on_receive_index_integer(index, value)
                elif size == 12:
                    index, value, date = bytes_to_index_integer_date(data)
                    if self.on_receive_index_integer_date:
                        self.on_receive_index_integer_date(index, value, date)
                elif size == 16:
                    index, value, date = bytes_to_index_integer_date(data)
                    if self.on_receive_index_integer_date:
                        self.on_receive_index_integer_date(index, value, date)
            except Exception as e:
                print("Error:", e)
                self.sock.close()
                break
        print("Wait for restart...")
       
       
       
## Websocket IID
### SEND WEBSOCKET IID         
# NOT TESTED YET
class NoAuthWebsocketIID:
    
    def __init__(self, ivp4, port):
        self.ivp4 = get_ipv4(ivp4)
        self.port = port
        self.uri = f"ws://{self.ivp4}:{self.port}"
        self.on_receive_integer = None
        self.on_receive_index_integer = None
        self.on_receive_index_integer_date = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())
        
    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            await self.listen(websocket)
            
    async def listen(self, websocket):
        async for message in websocket:
            data = message.encode('latin1')
            size = len(data)
            if size == 4:
                value = bytes_to_int(data)
                if self.on_receive_integer:
                    self.on_receive_integer(value)
            elif size == 8:
                index, value = bytes_to_index_integer(data)
                if self.on_receive_index_integer:
                    self.on_receive_index_integer(index, value)
            elif size == 12:
                index, value, date = bytes_to_index_integer_date(data)
                if self.on_receive_index_integer_date:
                    self.on_receive_index_integer_date(index, value, date)
            elif size == 16:
                index, value, date = bytes_to_index_integer_date(data)
                if self.on_receive_index_integer_date:
                    self.on_receive_index_integer_date(index, value, date)
            
 # ## Websocket IID
### RECEIVE WEBSOCKET ECHO IID
# NOT TESTED YET
class NoAuthServerWebSocketEchoIID:
    def __init__(self, ivp4:str, port:int, bool_print_debug:bool):
        self.ivp4 = get_ipv4(ivp4)
        self.port = port
        self.bool_print_debug = bool_print_debug
        self.uri = f"ws://{self.ivp4}:{str(self.port)}"
        if self.bool_print_debug:
            print (f"Websocket IID Echo Server: {self.uri}")
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.start_server())

    async def start_server(self):
        async with websockets.serve(self.echo, self.ivp4, self.port):
            await asyncio.Future()  # run forever

    async def echo(self, websocket, path):
        if self.bool_print_debug:
            print (f"Websocket IID Echo Server: {self.uri} connected")
        async for message in websocket:
            size = len(message)
            if size == 4 or size == 8 or size == 12 or size == 16:
                if self.bool_print_debug:
                    print (f"Received: {message}")
                await websocket.send(message)
                




"""
python -m build
pip install .\dist\iid42-2025.1.8.2-py3-none-any.whl --force-reinstall

pip install --upgrade twine
python -m twine upload dist/*
pip install iid42 --force-reinstall

"""


class HelloWorldIID:
    def hello_world():
        print("Hello, World!")
        
    def push_my_first_iid():
        print("Push My First IID")
        target = SendUdpIID("127.0.0.1",3615,True)
        target.push_integer(42)
        target.push_index_integer(0,2501)
        target.push_index_integer_date_ntp_now(1,1001)
        target.push_index_integer_date_ntp_in_milliseconds(2,2001,1000)
        
        
    def console_loop_to_push_iid_with_params(ivp4:str, port:int):
        print("Console Loop To Push IID")
        target= SendUdpIID(ivp4, port,True)
        print ("Enter 'exit' to stop")
        print ("i: 42 (For integer)")
        print ("ii: 0, 42 (For index integer)")
        print ("iid: 5, 1000, 50 (Push inex 5 integer 1000 to press with a delay request of 50ms)")
        print ("iid: 5, 2000, 500 (Push inex 5 integer 2000 to release with a delay request of 500ms)")
        
        while True:
            text= input("Enter IID Text: ")
            target.push_integer_as_shorcut(text)    
        
    def console_loop_to_push_iid_local():
        HelloWorldIID.console_loop_to_push_iid_with_params("127.0.0.1",3615)
        
    def console_loop_to_push_iid_ddns(target_ddns:str):
        port = 3615
        ipv4 = socket.gethostbyname(target_ddns)
        HelloWorldIID.console_loop_to_push_iid_with_params(ipv4,port)
        
    
    def console_loop_to_push_iid_apintio():
        """
        This allows to twitch play in python when EloiTeaching is streaming with UDP activated.
        
        """
        # NOTE: UDP on APINT.IO is only available on port 3615 when a Twitch Play is occuring
        # See Py Pi apintio for ddns name and tools
        HelloWorldIID.console_loop_to_push_iid_ddns("apint-gaming.ddns.net")
        # See no-ip.com for creating a ddns name for your own IP address
    

    
        
if __name__ == "__main__":
    
    HelloWorldIID.push_my_first_iid()
    HelloWorldIID.console_loop_to_push_iid_apintio()
    