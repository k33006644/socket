#simple websockets server
import serial
import threading
import asyncio
import websockets
import time
import socket
import pickle

clients = []
data='' #global var for client to read
data_raw=''

#not used in GPIO version

def serMonitor():
	global semaphor,clients
	ser = serial.Serial("COM4", 57600) 
	threshold=700 #門檻值
	while semaphor:
		try:
			while ser.in_waiting:          # 若收到序列資料…
				data_raw = ser.readline()  # 讀取一行
				#################################################
				if int(data_raw) > threshold: #若大於門檻值
					for client in clients: 
						try:
							msg=b"CO2 " + data_raw #可以自己定義送出的格式, 到client端再解回來
							client.sendall(msg) #主動送給client
						except:
							pass #若出錯則跳過
				######################################################
				#print('連到了')            #測試
				#data = data_raw  #data_raw.decode()   # 用預設的UTF-8解碼
				#data = data_raw.hex()
				#print('接收到的原始資料：', data_raw)
				#print('接收到的資料：', data)
			time.sleep(0.1) #sleep a while if necessary
		except Exception as e:
			print("Exception", e)
			pass
			ser.close()    # 清除序列通訊物件
			print('再見！')
	#end while
	ser.close()
	
def start_socket_server():
    t = threading.Thread(target=wait_for_socket_connection)
    t.start()

def wait_for_socket_connection():
    bind_ip = "localhost"
    bind_port = 4545
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((bind_ip,bind_port))
        s.listen()
        
        while True:
            conn, address = s.accept()
            ########################################
			clients.append(conn) #append this client to list
			##########################################
            client_handler = threading.Thread(
                target = receive_socket_message,
                args=(conn, address)
            )
            client_handler.start()
            
def receive_socket_message(connection, address):
    with connection:
        print(f'Connected by: {address}')
        while True:
            message = connection.recv(1024)
            
            # try:
            #     parsed_message = pickle.loads(message)
            # except Exception:
            #     print(f"{message} caanot be parsed")
            
            parsed_message = message.decode('UTF-8')

            if message:
                # print("Message: " + message)
                print("Parsed_message: " + parsed_message)
                if parsed_message == "GET":
                    print('YES')
                    data = "DDATA!"
                    send_message = str.encode(data)
                    connection.send(send_message)
	
semaphor=1 #semaphor for the monitoring thread
	
try:
	#start the serial montor thread
	start_socket_server()
	threading.Thread(target=serMonitor).start()#Arduino
	#start the socker server for client query
	#asyncio.get_event_loop().run_until_complete(
	#asyncio.get_event_loop().run_forever()#57-59可不用
except KeyboardInterrupt:
	semaphor=0 #tell the thread to end
	time.sleep(5) #wait a while for the thread to end