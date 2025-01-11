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


class IIDUtility:
    default_ntp_server = "be.pool.ntp.org"
    default_global_ntp_offset_in_milliseconds = 0



    def is_text_ivp4(server_name:str):
        # check if the string is in 255.255.255.255 format
        pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        return bool(pattern.match(server_name))

    def get_ipv4(server_name:str):
        if IIDUtility.is_text_ivp4(server_name):
            return server_name
        ivp4 = socket.gethostbyname(server_name)
        return ivp4
    
    def get_default_global_ntp_offset_in_milliseconds():
        return default_global_ntp_offset_in_milliseconds

        
    def bytes_to_int(bytes:bytes):
        value= struct.unpack('<i', bytes)[0]
        return value

    def bytes_to_index_integer(bytes:bytes):
        index, value = struct.unpack('<ii', bytes)
        return index, value
    
    def bytes_to_index_date(bytes:bytes):
        index, date = struct.unpack('<iQ', bytes)
        return index, date

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
                return IIDUtility.integer_to_bytes(integer)
            elif text.startswith("ii:"):
                index, integer = text.split(":")[1].split(",")
                return IIDUtility.index_integer_to_bytes(int(index), int(integer))
            elif text.startswith("iid:"):
                index, integer, delay = text.split(":")[1].split(",")
                
                return IIDUtility.index_integer_now_relay_milliseconds_to_bytes(int(index), int(integer), int(delay))
            else:
                while "  " in text:
                    text = text.replace("  ", " ")
                tokens : list = text.replace(",", " ").split(" ")
                size = len(tokens)
                if size == 1:
                    integer = int(text)
                    return IIDUtility.integer_to_bytes(integer)
                elif size == 2:
                    index = int(tokens[0])
                    integer = int(tokens[1])
                    return IIDUtility.index_integer_to_bytes(index, integer)
                elif size == 3:
                    index = int(tokens[0])
                    integer = int(tokens[1])
                    delay = int(tokens[2])
                    return IIDUtility.index_integer_now_relay_milliseconds_to_bytes(index, integer, delay)
                else:
                    integer = int(text)
                    return IIDUtility.integer_to_bytes(integer)
        except Exception as e:
            print("Error", e)    
        return None
            
    def get_random_integer(from_value:int, to_value:int):
        return random.randint(from_value, to_value)
    def get_random_integer_100():
        return IIDUtility.get_random_integer(0, 100)
    def get_random_integer_int_max():
        return IIDUtility.get_random_integer(-2147483647, 2147483647)

    def get_random_integer_int_max_positive():
        return IIDUtility.get_random_integer(0, 2147483647)
            
    def i(integer_value:int):
        return IIDUtility.integer_to_bytes(integer_value)

    def ii(index:int, integer_value:int):
        return IIDUtility.index_integer_to_bytes(index, integer_value)

    def iid(index:int, integer_value:int, date:int):
        return IIDUtility.index_integer_date_to_bytes(index, integer_value, date)

    def iid_ms(index:int, integer_value:int, milliseconds:int):
        return IIDUtility.index_integer_date_to_bytes(index, integer_value, milliseconds)
    
    



class NtpOffsetFetcher: 
       
    default_global_ntp_offset_in_milliseconds = 0
    
    def fetch_ntp_offset_in_milliseconds( ntp_server):
        try:
            c = ntplib.NTPClient()
            response = c.request(ntp_server)
            return response.offset*1000
        except Exception as e:
            print(f"Error NTP Fetch: {ntp_server}", e)
            return 0


    def set_global_ntp_offset_in_milliseconds(ntp_server=IIDUtility.default_ntp_server):

        try:
            offset=  NtpOffsetFetcher.fetch_ntp_offset_in_milliseconds(ntp_server)
            global default_global_ntp_offset_in_milliseconds
            default_global_ntp_offset_in_milliseconds = offset
            print (f"Default Global NTP Offset: {default_global_ntp_offset_in_milliseconds} {ntp_server}" )
        except Exception as e:
            pass
            default_global_ntp_offset_in_milliseconds = 0
    def get_global_ntp_offset_in_milliseconds():
        return int(default_global_ntp_offset_in_milliseconds)
            
NtpOffsetFetcher.set_global_ntp_offset_in_milliseconds()
    

## UDP IID
### SEND UDP IID
class SendUdpIID:
    
    
  

    
    def __init__(self, ivp4, port, use_ntp:bool, use_queue_thread:bool=False):
        
        self.ivp4 = IIDUtility.get_ipv4(ivp4)
        self.port = port
        self.ntp_offset_local_to_server_in_milliseconds=0
        
        if use_queue_thread:
            
            self.callback =IntegerTimeQueueHolder.BytesActionDelegate(self.push_bytes)
            self.queue_thread= IntegerTimeQueueHolder(self.callback, 1)
            
        
        
        if use_ntp:
            self.fetch_ntp_offset()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
 
        
    def get_ntp_offset(self):
        return self.ntp_offset_local_to_server_in_milliseconds
        
    def push_integer_as_shorcut(self, text:str):
        bytes = IIDUtility. text_shortcut_to_bytes(text)
        if bytes:
            self.sock.sendto(bytes, (self.ivp4, self.port))
    def push_bytes(self, bytes:bytes):
        
        print (f"Push Bytes: {self.ivp4} {self.port} {bytes}")
        self.sock.sendto(bytes, (self.ivp4, self.port))
        
    def push_text(self, text:str):
        self.push_bytes(text.encode('utf-8'))
        
    def push_integer(self, value:int):
        self.push_bytes(IIDUtility. integer_to_bytes(value))
        
    def push_index_integer(self, index:int, value:int):
        self.push_bytes(IIDUtility. index_integer_to_bytes(index, value))
        
    def push_index_integer_date(self, index:int, value:int, date:int):
        self.push_bytes(IIDUtility.index_integer_date_to_bytes(index, value, date))
        
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
        
        
    def is_using_queue_thread(self):
        return self.queue_thread is not None
    
    def push_integer_in_queue(self, value:int, delay_in_milliseconds:int):
        self.queue_thread.push_bytes_to_queue(IIDUtility.integer_to_bytes(value), delay_in_milliseconds)
    def push_index_integer_in_queue(self, index:int, value:int, delay_in_milliseconds:int):
        self.queue_thread.push_bytes_to_queue(IIDUtility.index_integer_to_bytes(index, value), delay_in_milliseconds)
    def clear_queue(self):
        self.queue_thread.clear_queue()
     


    
    



## UDP IID
### RECEIVE UDP IID
class ListenUdpIID:
    def __init__(self, ivp4, port, ntp_offset_in_milliseconds:int=0, integer_to_sync_ntp:int=1259):
        self.ivp4 = IIDUtility.get_ipv4(ivp4)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ivp4, self.port))
        self.on_receive_integer = None
        self.on_receive_index_integer = None
        self.on_receive_index_integer_date = None
        self.on_received_integer_date = None
        self.ntp_offset_in_milliseconds = ntp_offset_in_milliseconds
        self.manual_adjustement_source_to_local_ntp_offset_in_milliseconds = 0
        
        ## Sync NTP is around 10-50 ms precision
        ## If you use a integer with ntp on the client and to set listener.
        ## You can adjust the offset to 1-2 ms precision
        self.integer_to_sync_ntp=integer_to_sync_ntp

        # DEFAULT DEBUG
        self.on_receive_index_integer_date = self.debug_received_index_integer_date
        self.on_receive_integer = self.debug_received_integer
        self.on_receive_index_integer = self.debug_received_index_integer
        self.on_received_integer_date = self.debug_received_integer_date
        
                
        
        # Start thread
        self.thread = threading.Thread(target=self.listen)
        self.thread.daemon = True
        self.thread.start()
        
        
    def debug_received_integer(self, value:int):
        print(f"Received Integer: {value} ")
        
    def debug_received_index_integer(self, index:int, value:int):
        print(f"Received Index Integer: {index} {value}")

    def debug_received_integer_date(self, value:int, date:int):
        time = self.get_ntp_time_in_milliseconds_with_manual_adustement()
        print(f"Received Integer Date: {value} {date} vs {time} dif {time -date} ")

    def debug_received_index_integer_date(self, index:int, value:int, date:int):
        time = self.get_ntp_time_in_milliseconds_with_manual_adustement()
        print(f"Received Index Integer Date: {index} {value} {date} vs {time} dif {time-date} ")

        
    def get_ntp_time_in_milliseconds(self):
        return int(time.time()*1000) + self.ntp_offset_in_milliseconds 
    
    def get_ntp_time_in_milliseconds_with_manual_adustement(self):
        return int(time.time()*1000) + self.ntp_offset_in_milliseconds  - self.manual_adjustement_source_to_local_ntp_offset_in_milliseconds
    
    def notify_integer(self, value:int):
        if self.on_receive_integer:
            self.on_receive_integer(value)
    def notify_index_integer(self, index:int, value:int):
        if self.on_receive_index_integer:
            self.on_receive_index_integer(index, value)
    def notify_index_integer_date(self, index:int, value:int, date:int):
        if self.on_receive_index_integer_date:
            self.on_receive_index_integer_date(index, value, date)
    def notify_integer_date(self, value:int, date:int):
        if self.on_received_integer_date:
            self.on_received_integer_date(value, date)
            
    def is_integer_sync_ntp_request(self, value:int):
        if self.integer_to_sync_ntp == 0:
            return False
        return value == self.integer_to_sync_ntp
    
    def request_to_sync_ntp(self, milliseconds_source, milliseconds_local):
        int_diff_source_to_local = (milliseconds_local- milliseconds_source)
        self.manual_adjustement_source_to_local_ntp_offset_in_milliseconds = int_diff_source_to_local
        
        
    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data is None:
                    continue
                size = len(data)
                if size == 4:
                    value = IIDUtility.bytes_to_int(data)
                    self.notify_integer(value)
                    
                elif size == 8:
                    index, value = IIDUtility.bytes_to_index_integer(data)
                    self.notify_index_integer(index, value)
                    
                elif size == 12:
                    value, date = IIDUtility.bytes_to_index_date(data)
                    if self.is_integer_sync_ntp_request(value):
                        self.request_to_sync_ntp(date, self.get_ntp_time_in_milliseconds())
                    self.notify_integer_date(value, date)
                    
                elif size == 16:
                    
                    index, value, date = IIDUtility.bytes_to_index_integer_date(data)
                    if self.is_integer_sync_ntp_request(value):
                        self.request_to_sync_ntp(date, self.get_ntp_time_in_milliseconds())
                    self.notify_index_integer_date(index, value, date)
                    
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
        self.ivp4 = IIDUtility.get_ipv4(ivp4)
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
                value = IIDUtility.bytes_to_int(data)
                if self.on_receive_integer:
                    self.on_receive_integer(value)
            elif size == 8:
                index, value = IIDUtility.bytes_to_index_integer(data)
                if self.on_receive_index_integer:
                    self.on_receive_index_integer(index, value)
            elif size == 12:
                index, value, date = IIDUtility.bytes_to_index_integer_date(data)
                if self.on_receive_index_integer_date:
                    self.on_receive_index_integer_date(index, value, date)
            elif size == 16:
                index, value, date = IIDUtility.bytes_to_index_integer_date(data)
                if self.on_receive_index_integer_date:
                    self.on_receive_index_integer_date(index, value, date)
            
 # ## Websocket IID
### RECEIVE WEBSOCKET ECHO IID
# NOT TESTED YET
class NoAuthServerWebSocketEchoIID:
    def __init__(self, ivp4:str, port:int, bool_print_debug:bool):
        self.ivp4 = IIDUtility.get_ipv4(ivp4)
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
    




















































class IntegerTimeQueueHolder:
    """
    This class holds a queue of integer actions represented as shortcut strings.
    The queue can be flushed if needed.
    Some code does not handle the datetime of the IID, so it is up to the client to manage it.
    Using NTP Date on the target is ideal due to its 1-5ms precision.
    Local date has transport latency but ensures the code is implemented and manageable in case of exceptions or errors.
    """
    
    def get_time_in_milliseconds():
        return time.time_ns() // 1_000_000
    
    class WaitingShortcut:
        def __init__(self, hold_bytes:bytes, time_in_milliseconds:int, delay_in_milliseconds:int ):
            self.hold_integer:bytes = hold_bytes
            self.local_time_created:int = time_in_milliseconds
            self.local_time_to_execute:int = time_in_milliseconds + delay_in_milliseconds
            
            
        
        def is_ready(self, current_time:int):
            return current_time >= self.local_time_to_execute
    
        def get_hold_bytes(self): 
            return self.hold_integer


    class QueueOfShortcuts:
        def __init__(self):
            self.list = list()
            
        def append_at_0(self, hold_bytes:bytes):
            self.list.insert(0, hold_bytes)
        
        def has_waiting_bytes(self):
            return len(self.list)>0
        
        def check_for_bytes_to_extract(self, current_time:int):
            list_result = list()
            int_index= len(self.list)-1
            while int_index>=0:
                shortcut = self.list[int_index]
                if shortcut.is_ready(current_time):
                    list_result.append(shortcut)
                    self.list.pop(int_index)
                int_index-=1
                
            return list_result

        def clear (self):
            self.list.clear()

    class BytesActionDelegate:
        def __init__(self, byte_handler):
            self.byte_handler = byte_handler
            
        def out_of_queue(self, bytes_to_push:bytes):
            print ("Bytes Out Of Queue: ", bytes_to_push)
            self.byte_handler(bytes_to_push)
            
    def __init__(self, handle_action:BytesActionDelegate, check_time_in_milliseconds:int):
        
        self.in_queue_bytes = IntegerTimeQueueHolder.QueueOfShortcuts()
        self.current_time:int = IntegerTimeQueueHolder.get_time_in_milliseconds()
        self.handle_action:IntegerTimeQueueHolder.BytesActionDelegate = handle_action
        self.start_loop_in_thread(check_time_in_milliseconds)
    

    def push_bytes_to_queue_at_localTime(self,hold_bytes:bytes, time_in_milliseconds:int, delay_in_milliseconds:int):
        self.in_queue_bytes.append_at_0(self.WaitingShortcut(hold_bytes, time_in_milliseconds, delay_in_milliseconds))
        print ("Pushed Bytes To Queue: ", hold_bytes, len(self.in_queue_bytes.list))
    def push_bytes_to_queue(self,hold_bytes:bytes, delay_in_milliseconds:int):
        self.push_bytes_to_queue_at_localTime(hold_bytes, IntegerTimeQueueHolder.get_time_in_milliseconds(), delay_in_milliseconds)
        


   

    def start_loop_in_thread(self, time_in_waiting_milliseconds:int):
        print ("Start Loop In Thread")
        t = threading.Thread(target=self.loop_for_thread_with_time, args=(time_in_waiting_milliseconds,))
        #t.daemon = True
        t.start()
        print ("Thread Started")
        
 

    def loop_for_thread_with_time(self, time_in_waiting_milliseconds:int):
        print ("Loop For Thread With Time")
        waiting_time_seconds = time_in_waiting_milliseconds/1000.0
        while True:
            self.check_the_queue_for_shortcuts()
            time.sleep(waiting_time_seconds)
        print ("Loop For Thread With Time End")
 

    def clear_queue(self):
        self.in_queue_bytes.clear()
        
    


    def check_the_queue_for_shortcuts(self):
        """
        Have to be called byt the timer of the user.
        We can't know if async, thread , time or else will be used.
        """

        
        if not self.in_queue_bytes.has_waiting_bytes():
            return
        
        self.current_time = IntegerTimeQueueHolder.get_time_in_milliseconds()
        for s in self.in_queue_bytes.check_for_bytes_to_extract(self.current_time):

            bytes_store:bytes = s.get_hold_bytes()
            print ("Extracted Bytes From Queue: ", bytes_store, len(self.in_queue_bytes.list))
            self.handle_action.out_of_queue(bytes_store)






















    
        
if __name__ == "__main__":

    NtpOffsetFetcher.set_global_ntp_offset_in_milliseconds()
    offset= NtpOffsetFetcher.get_global_ntp_offset_in_milliseconds()
    print (f"Default Global NTP Offset: {offset}")

    bool_loop_listener_test = True
    if bool_loop_listener_test:
        print("Loop Listener Test")
        target = ListenUdpIID("0.0.0.0",3615, offset)
      
        

    bool_console_test = False
    if bool_console_test : 
        print("Console Test")      
        HelloWorldIID.push_my_first_iid()
        HelloWorldIID.console_loop_to_push_iid_apintio()
        
    bool_queue_test = False
    if bool_queue_test:
        print("Queue Test")
        target = SendUdpIID("apint.ddns.net",3615,True,True)
        print("IVP4", target.ivp4)
        target.push_index_integer_in_queue(1,1082,0)
        target.push_index_integer_in_queue(1,2082,1000)
        target.push_index_integer_in_queue(1,1037,2000)
        target.push_index_integer_in_queue(1,2037,4000)
        target.push_index_integer_in_queue(1,1038,5000)
        target.push_index_integer_in_queue(1,2038,6000)
        target.push_index_integer_in_queue(1,1039,7000)
        target.push_index_integer_in_queue(1,2039,8000)
        
        target.push_integer_in_queue(2082,11000)
        target.push_integer_in_queue(1037,12000)
        target.push_integer_in_queue(2037,14000)
        target.push_integer_in_queue(1038,15000)
        target.push_integer_in_queue(2038,16000)
        target.push_integer_in_queue(1039,17000)
        target.push_integer_in_queue(2039,18000)
        
    
    while(True):
        text = input("Enter IID Text: ")
        if text == "exit":
            break