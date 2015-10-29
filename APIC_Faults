
import requests
import json
import xmltodict
from operator import attrgetter
import sys
import acitoolkit.acitoolkit as ACI

##Objs

class credentials:
    def __init__(self,ip,user,password,session):
        self.ip = ip
        self.password = password
        self.username = user
        self.session = session

class faults:
    def __init__(self,dict):   
        self.cause = dict["@cause"]
        self.childAction = dict["@childAction"]
        self.code = dict["@code"]
        self.count = dict["@count"]
        self.descr = dict["@descr"]
        self.dn = dict["@dn"]
        self.domain = dict["@domain"]
        self.rule = dict["@rule"]
        self.severity = dict["@severity"]
        self.status = dict["@status"]
        self.subject = dict["@subject"]
        self.type = dict["@type"]

class interface:
    def __init__(self,dic,creds):
        self.creds = creds
        self.dic = dic
        self.name = "eth " + dic["@dn"].replace("topology/pod-","").replace("node-","").replace("sys/phys-[eth","").replace("]","")
    
        self.childQuery = "/api/node/mo/" + dic["@dn"] + ".xml?query-target=children"
        self.child = childStats(self.childQuery,self.creds)

        
class childStats:
    def __init__(self,query,creds):
        self.creds = creds
        self.query = query
        self.json = xmltodict.parse(creds.session.get("https://" + creds.ip + query, verify=False).content)["imdata"]["ethpmPhysIf"]
        
##/objs   
     
def getErrorsEgressDrops():

# Login to APIC
    session = ACI.Session("https://172.31.216.24", "admin", "scotch123",subscription_enabled = False)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)

    # Download all of the interfaces and get their stats
    # and display the stats

    interfaces = ACI.Interface.get(session)
    allStats =[]
    avgErrorPerInt = []
    for interface in sorted(interfaces, key=attrgetter('if_name')):
        if "egrDropPkts" in interface.stats.get().keys():
            stats = interface.stats.get()['egrDropPkts']
        if stats:
            allStats.append([interface.name,stats["5min"]])
    for i in  allStats:
            #avg packets dropped cause full buffer
            name = i[0]
            drops = i[1][12]['bufferAvg']
            if drops:
                avgErrorPerInt.append([name,drops])
    return avgErrorPerInt


def get_ints(xml):
    jsonPorts = xmltodict.parse(xml)
    return jsonPorts["imdata"]["l1PhysIf"]



def main():
    with requests.Session() as s:
        login = "<aaaUser name='admin' pwd='scotch123'/>"
        r = s.post('https://172.31.216.24/api/aaaLogin.xml', data = login, verify=False)
        r = s.get('https://172.31.216.24/api/node/class/l1PhysIf.xml?')    
        faultsC  = s.get('https://172.31.216.24/api/node/class/faultSummary.xml?')
        faultsJson = xmltodict.parse(faultsC.content)
        
        faultList = []
        for f in faultsJson['imdata']["faultSummary"]:
            fobj = faults(f)
            faultList.append(fobj)
    
        credsObj = credentials("172.31.216.24","admin","scotch123",s)
        ints = get_ints(r.content)
        interfacesObjList = []
    
        resetCountThreshold = 3
        resets = []
        buffDrops = getErrorsEgressDrops()
        for i in ints:
            singelIntObj = interface(i,credsObj)
            interfacesObjList.append(singelIntObj)
        for i in interfacesObjList:
            if i.dic["@adminSt"] == "up" and "epg" in i.child.json["@usage"]:
                if int(i.child.json["@resetCtr"]) >= resetCountThreshold:
                    resets.append(i)
        for f in faultList:
            print "FAULT: ",f.severity, f.count, f.code, f.descr
        for device in resets:
            print  "RESET FAULT: ", "Reset Count:", device.child.json["@resetCtr"], device.name
        for d in buffDrops:
            print "Avg Drops from Buffer Overflow during 5min interval:",d[0],d[1]
    
        
if __name__ == '__main__':
    main()
