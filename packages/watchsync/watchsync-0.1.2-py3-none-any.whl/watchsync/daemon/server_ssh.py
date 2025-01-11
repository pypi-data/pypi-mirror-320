import os
import paramiko
import socket
import sys
import threading

# Configuración del servidor SSH
HOST_KEY = paramiko.RSAKey(filename='/home/rlizana/.ssh/id_rsa')
AUTHORIZED_KEYS = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDEiEg2U3373PTqRgv0XtBx2bLaeM+8m5pQMaV+OEG+KuhFl/Pi3aD4/XlsffdtISI8YEjWZIaagdQ2ZqOzDdMkQXZfvh6r0pC1Bi2MxNaTfWa6oEXJ6Yh4xAwNYpZOwBiZfbG1NcJUmN1lRrqiTwetdCqaZhK+x8xl7QyHfaTvPNhmiJPOZLIWFj6aEgx4ddJgWlKivUPv0mMdehH1DhxfCA6KPImbBDvViLYUCfzHPC78lWz//FAOM0OHVHbMeBBwuD7KoGiFYIsT9PAh721sbKN/de7gLs2wTTxsgFNit/lHGUr4h2HQ/fZ5BQlRlClIv753yeEEpiGAW4VB9mf7 rlizana@rlizana'

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        with open(AUTHORIZED_KEYS) as f:
            authorized_keys = f.read().splitlines()
        if key.get_base64() in authorized_keys:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return True

def handle_client(client):
    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)
    server = Server()
    transport.start_server(server=server)

    channel = transport.accept(20)
    if channel is None:
        print('No channel.')
        return

    server.event.wait(10)
    if not server.event.is_set():
        print('No exec request.')
        return

    while True:
        data = channel.recv(1024)
        if not data:
            break
        print(data.decode('utf-8'))
        channel.send(data)

    channel.close()
    transport.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2200))
    server_socket.listen(100)

    print('Listening for connection ...')
    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr}')
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == '__main__':
    print('Starting SSH server ...')
    main()
