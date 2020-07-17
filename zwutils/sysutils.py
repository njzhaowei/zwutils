import re
import psutil

def pids_by_name(nm=None):
    rtn = []
    for proc in psutil.process_iter(['pid', 'name']):
        pinfo = proc.info
        pname = pinfo['name']
        if nm:
            arr = re.findall(pname, nm)
            if len(arr)>0:
                rtn.append(pinfo)
                continue
        else:
            rtn.append(pinfo)
    return rtn
            

