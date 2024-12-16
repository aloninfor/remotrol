import paramiko
import subprocess

def connect_ssh(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password)
    client.close()

def connect_rdp(host, port, username, password):
    subprocess.run(['xfreerdp', f'/u:{username}', f'/p:{password}', f'/v:{host}:{port}'])

def connect_vnc(host, port, password):
    subprocess.run(['vncviewer', f'{host}:{port}', f'-passwd={password}'])
