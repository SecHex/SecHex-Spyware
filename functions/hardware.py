import os
import socket
import uuid
import psutil
import cpuinfo
import platform




def get_tasks():
    tasks = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            pid = process.info['pid']
            name = process.info['name']
            tasks.append({'pid': pid, 'name': name})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return tasks

def is_running_on_vm():
    vm_indicator_keys = ['hypervisor_vendor_id', 'vmware', 'virtualbox']
    try:
        cpu_info = cpuinfo.get_cpu_info()
        for key in vm_indicator_keys:
            if key in cpu_info:
                return 'Yes'
    except:
        pass
    return 'No'


def get_system_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
        for ele in range(0, 8*6, 8)][::-1])
    hwid = os.getenv('COMPUTERNAME')
    memory = f"{psutil.virtual_memory().total // (1024 ** 3)}GB"
    os_name = platform.system()
    os_version = platform.release()
    cpu_name = cpuinfo.get_cpu_info()['brand_raw']
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq().current / 1000

    try:
        import GPUtil
        GPUs = GPUtil.getGPUs()
        gpu = f"{GPUs[0].name}, {GPUs[0].memoryTotal}MB"
    except ImportError:
        pass
    system_info = {
        'ip_address': ip_address,
        'mac_address': mac_address,
        'pc_name': hwid,
        'memory': memory,
        'os_name': os_name,
        'os_version': os_version,
        'cpu_name': cpu_name,
        'cpu_cores': cpu_cores,
        'cpu_freq': cpu_freq,
        'is_running_on_vm': is_running_on_vm()
    }
    return system_info
