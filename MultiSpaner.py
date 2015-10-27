#!/usr/bin/env python

import threading
import Queue
import time
from device import Device
import xmltodict
import urllib2
import time

queue = Queue.Queue()
queueError = Queue.Queue()
queueSuccess = Queue.Queue()
threadQueue = Queue.Queue()
outlock = threading.Lock()

class interface:
	def __init__(self,intName):
		self.interface=intName
		self.state = ""
		self.eth_outrate1_bits= 0
		self.eth_outrate1_pkts= 0
		self.eth_inucast= 0
		self.eth_inmcast= 0
		self.eth_inbcast= 0
		self.eth_inpkts= 0
		self.eth_inbytes= 0
		self.eth_jumbo_inpkts= 0
		self.eth_storm_supp= 0
		self.eth_runts= 0
		self.eth_giants= 0
		self.eth_crc= 0
		self.eth_nobuf= 0
		self.eth_inerr= 0
		self.eth_frame= 0
		self.eth_overrun= 0
		self.eth_underrun= 0
		self.eth_ignored= 0
		self.eth_watchdog= 0
		self.eth_bad_eth= 0
		self.eth_bad_proto= 0
		self.eth_in_ifdown_drops= 0
		self.eth_dribble= 0
		self.eth_indiscard= 0
		self.eth_inpause= 0
		self.eth_outucast= 0
		self.eth_outmcast= 0
		self.eth_outbcast= 0
		self.eth_outpkts= 0
		self.eth_outbytes= 0
		self.eth_jumbo_outpkts= 0
		self.eth_outerr= 0
		self.eth_coll= 0
		self.eth_deferred= 0
		self.eth_latecoll= 0
		self.eth_lostcarrier= 0
		self.eth_nocarrier= 0
		self.eth_babbles= 0
		self.eth_outdiscard= 0
		self.eth_outpause= 0
	def populateCounters(self,singleIntDic):
			try:
				self.state = singleIntDic["state"]
				self.eth_outrate1_bits= int(singleIntDic["eth_outrate1_bits"])
				self.eth_outrate1_pkts= int(singleIntDic["eth_outrate1_pkts"])
				self.eth_inucast= int(singleIntDic["eth_inucast"])
				self.eth_inmcast= int(singleIntDic["eth_inmcast"])
				self.eth_inbcast= int(singleIntDic["eth_inbcast"])
				self.eth_inpkts= int(singleIntDic["eth_inpkts"])
				self.eth_inbytes= int(singleIntDic["eth_inbytes"])
				self.eth_jumbo_inpkts= int(singleIntDic["eth_jumbo_inpkts"])
				self.eth_storm_supp= int(singleIntDic["eth_storm_supp"])
				self.eth_runts= int(singleIntDic["eth_runts"])
				self.eth_giants= int(singleIntDic["eth_giants"])
				self.eth_crc= int(singleIntDic["eth_crc"])
				self.eth_nobuf= int(singleIntDic["eth_nobuf"])
				self.eth_inerr= int(singleIntDic["eth_inerr"])
				self.eth_frame= int(singleIntDic["eth_frame"])
				self.eth_overrun= int(singleIntDic["eth_overrun"])
				self.eth_underrun= int(singleIntDic["eth_underrun"])
				self.eth_ignored= int(singleIntDic["eth_ignored"])
				self.eth_watchdog= int(singleIntDic["eth_watchdog"])
				self.eth_bad_eth= int(singleIntDic["eth_bad_eth"])
				self.eth_bad_proto= int(singleIntDic["eth_bad_proto"])
				self.eth_in_ifdown_drops= int(singleIntDic["eth_in_ifdown_drops"])
				self.eth_dribble= int(singleIntDic["eth_dribble"])
				self.eth_indiscard= int(singleIntDic["eth_indiscard"])
				self.eth_inpause= int(singleIntDic["eth_inpause"])
				self.eth_outucast= int(singleIntDic["eth_outucast"])
				self.eth_outmcast= int(singleIntDic["eth_outmcast"])
				self.eth_outbcast= int(singleIntDic["eth_outbcast"])
				self.eth_outpkts= int(singleIntDic["eth_outpkts"])
				self.eth_outbytes= int(singleIntDic["eth_outbytes"])
				self.eth_jumbo_outpkts= int(singleIntDic["eth_jumbo_outpkts"])
				self.eth_outerr= int(singleIntDic["eth_outerr"])
				self.eth_coll= int(singleIntDic["eth_coll"])
				self.eth_deferred= int(singleIntDic["eth_deferred"])
				self.eth_latecoll= int(singleIntDic["eth_latecoll"])
				self.eth_lostcarrier= int(singleIntDic["eth_lostcarrier"])
				self.eth_nocarrier= int(singleIntDic["eth_nocarrier"])
				self.eth_babbles= int(singleIntDic["eth_babbles"])
				self.eth_outdiscard= int(singleIntDic["eth_outdiscard"])
				self.eth_outpause= int(singleIntDic["eth_outpause"])
			except Exception as e:
				#print "\t\t\tError storing info in exceptions:",e, self.interface
				pass
class root_Device:
	def __init__(self,hostname,proccesor_ID,version,connectedOn,user,pw):
		self.proccesor_ID = proccesor_ID
		self.connectedOn = connectedOn
		self.username = user
		self.password = pw
		self.hostname = hostname
		self.version = version
		self.ipIntBrief = []
		self.vrfList = []
		self.intStatus = []
		self.portChannels = []
		self.neighbors = []
		self.interfaceCounters = None
	def addNeighbor(self,neighbor):
		self.neighbors.append(neighbor)
	def addIp(self,ip):
		self.ipIntBrief.append(ip)
	def addIntStatus(self,interface):
		self.intStatus.append(interface)
	def addVrf(self,vrf):
		self.vrfList.append(vrf)
	def addPortChannel(self,channel):
		self.portChannels.append(channel)	
	def updateInterfaceCounters(self,intObj):
		self.interfaceCounters = intObj

class Neighbors:
	def __init__(self,NeighborRootDevice,NeighborDict):
		self.rootDevice = NeighborRootDevice
		self.NeighborDict = NeighborDict

class Vrf:                    
	def __init__(self,name):
		self.prefixList = []
		self.name = name     
	def addPrefix(self,prefix):
		self.prefixList.append(prefix)

def get_cdp_info(sw1):
	sh_neigh = sw1.show('show cdp neighbor detail')
	sh_neigh_dict = xmltodict.parse(sh_neigh[1])
	neighbors = sh_neigh_dict['ins_api']['outputs']['output']['body']["TABLE_cdp_neighbor_detail_info"]['ROW_cdp_neighbor_detail_info']
	return neighbors

def get_portchannel_sum(sw1):
	sh_chan = sw1.show('show port-channel summary')
	sh_chan_dict = xmltodict.parse(sh_chan[1])

	if sh_chan_dict['ins_api']['outputs']['output']['body'] != None:
		portChannels = sh_chan_dict['ins_api']['outputs']['output']['body']["TABLE_channel"]['ROW_channel']
		return portChannels

def get_hostname_serial_version(sw1):
	sh_ver= sw1.show('show version')
	sh_ver_dict = xmltodict.parse(sh_ver[1])
	proccesor_ID = sh_ver_dict['ins_api']['outputs']['output']['body']["proc_board_id"]
	hostname = sh_ver_dict['ins_api']['outputs']['output']['body']["host_name"]
	version = sh_ver_dict['ins_api']['outputs']['output']['body']["kickstart_ver_str"]
	return hostname,proccesor_ID,version

def get_ip_int_b(sw1):
	sh_ip_b =  sw1.show('show ip int brief')
	sh_ip_b_dict = xmltodict.parse(sh_ip_b[1])
	int_brief = sh_ip_b_dict['ins_api']['outputs']['output']['body']["TABLE_intf"]
	return int_brief

def get_vrf(sw1):
	sh_ip_vrf = sw1.show("sh ip route vrf all")
	sh_ip_vrf_dict = xmltodict.parse(sh_ip_vrf[1])
	sh_vrf = sh_ip_vrf_dict['ins_api']['outputs']['output']['body']["TABLE_vrf"]["ROW_vrf"]
	return sh_vrf

def get_int_status(sw1):
	sh_status =  sw1.show('show interface status')
	sh_status_dict = xmltodict.parse(sh_status[1])
	int_status = sh_status_dict['ins_api']['outputs']['output']['body']["TABLE_interface"]["ROW_interface"]
	return int_status

def get_int(sw1):
	sh_int =  sw1.show('show interface')
	sh_int_dict = xmltodict.parse(sh_int[1])
	interfaces = sh_int_dict['ins_api']['outputs']['output']['body']["TABLE_interface"]["ROW_interface"]
	return interfaces



def crawlDevice(ip_address,user,pw):
	sw1 = Device(ip=ip_address, username=user, password=pw)
	sw1.open()

	# Getting everything into dicts
	sh_vrf = get_vrf(sw1)
	int_brief = get_ip_int_b(sw1)
	int_status = get_int_status(sw1)
	hostname,proccesor_ID,version = get_hostname_serial_version(sw1)
	neighbors = get_cdp_info(sw1)
	port_channels = get_portchannel_sum(sw1)
	# Adding all data into objs
	LocalDevice = root_Device(hostname,proccesor_ID,version,ip_address,user,pw)

	for singleVrf in sh_vrf:
		vrf = Vrf(singleVrf["vrf-name-out"])
		if "TABLE_prefix" in singleVrf["TABLE_addrf"][ "ROW_addrf"].keys():
			for prefixes in singleVrf["TABLE_addrf"][ "ROW_addrf"]["TABLE_prefix"]["ROW_prefix"]:
				vrf.addPrefix(prefixes["ipprefix"])
			LocalDevice.addVrf(vrf)

	for ipInter in int_brief:
		LocalDevice.addIp(ipInter["ROW_intf"]["prefix"])

	LocalDevice.addPortChannel(port_channels)
	for interface in int_status:
		LocalDevice.addIp(interface)

	for neighbor in neighbors:
		neighEntry = Neighbors(root_Device,neighbor)
		LocalDevice.addNeighbor(neighEntry)



	return LocalDevice

def info_crawl(seedIp,user,password):
	discoveredObjs =[]
	crawledSerials = []
	uncrawled=[seedIp]
	crawledIps =[]
	for ipN in uncrawled:
		try:
			if ipN  not in crawledIps:
				newD = crawlDevice(ipN, user, password)
				crawledIps.append(ipN)
				print "Connection established to:", ipN
				if newD.proccesor_ID not in crawledSerials:
					crawledSerials.append(newD.proccesor_ID)
					discoveredObjs.append(newD)
					for neigh in newD.neighbors:
						neighborIp = (str(neigh.NeighborDict["v4mgmtaddr"]))
						if neighborIp not in uncrawled:
							uncrawled.append(neighborIp)
						print "\t",neigh.NeighborDict["v4mgmtaddr"], "DISCOVERED"	
		except urllib2.HTTPError:
			print "[!]Cannont establish to:",ipN
		except Exception as e:
			print "[!]ERROR: ",e
	print "--------CDP Crawl Complete--------\n"
	return discoveredObjs



def mon_device(device,seconds,tabs,destinationIp):
	threadQueue.put(1)
	destIp = destinationIp
	tabs = tabs*2
	deviceIp = device.connectedOn
	username = device.username
	passwor = device.password
	sw1 = Device(ip=deviceIp, username=username, password=passwor)
	sw1.open()

	flag = True
	print "Monitoring:",deviceIp
	try:
		while flag:
			allPack = []
			interfacers = get_int(sw1)
			device.updateInterfaceCounters(interfacers)
			for i in  interfacers:
				x = interface(i["interface"])
				x.populateCounters(i)
				#if x.eth_giants > 0 or x.eth_jumbo_inpkts > 0 or x.eth_crc > 0 or x.eth_giants or x.eth_inerr:
				if x.eth_outpkts > 1000:
					print ("-" * tabs)+ "Over 1000 on ", x.interface, x.eth_outpkts,deviceIp
					create_span = sw1.conf(" conf t ; monitor session 30 type erspan-source ; description ERSPAN30 for TEST ; source interface " + x.interface + " both ; destination ip " + destIp + " ; vrf default ; erspan-id 30 ; ip ttl 64 ; ip prec 0 ; ip dscp 0 ; mtu 1500 ; header-type 2 ; no shut ; end ;")
					print ("-" * tabs) + "Beginning erspan for", seconds ,"seconds","to",deviceIp,"on int",x.interface
					time.sleep(10)
					print ("-" * tabs) + "Done capturing, now Cleaning config",deviceIp,"on int",x.interface
					clean = sw1.conf("config t ;" + " no monitor session 30 ; end")
					clearing_counters = sw1.conf("clear counters interface" + x.interface)
					print ("-" * tabs) + "Done Cleaning, erspan sent to", destIp, "from",deviceIp, "-", x.interface
					# Remove flag for continous moitoring, with flag on it stops after the interface is noticed
					#flag = False
				else:
					allPack.append([x.eth_outpkts,x.interface])
			# 	if x.state == "up" and "Ether" in x.interface:
			# 		print x.interface, x.state, x.eth_outpkts
			time.sleep(3)
			ints = []
			interf = []
			for i in allPack:
				ints.append(i[0])
				interf.append(i[1])
			maxInt = max(ints)
			maxInterface = interf[ints.index(maxInt)]
			print ("-" * tabs) + "Highest packet count is", maxInt, "that is under 1000 on",maxInterface
	except (KeyboardInterrupt, SystemExit):
		print ("-" * tabs) + "Keyboard Interrupt, Forcing cleaning of",deviceIp
		clean = sw1.conf("config t ;" + " no monitor session 30 ; end")
		print ("-" * tabs) + "Done Cleaning, erspan sent to", destIp, "from",deviceIp,
	queue.put("RANDOM DATA FOR QUEUE")         
	threadQueue.get(False, 2)
	

def threadWrapper(deviceList,seconds,destinationIp,threadNumber):
    time1 = time.time()
    
    # Holds all the threads that will be created
    threads = []

    for device in deviceList:
    	tabs = deviceList.index(device)
        # Limits threads to threadNumber, if you go over with queue size, it will sleep for 10 seconds then check again.
        while threadQueue.qsize() > threadNumber: #thread limiter loop
            #Sleeps
            time.sleep(10)
        # Target is your function to run in parrel, and args are the arguments for the function
        t = threading.Thread( target=mon_device,args=(device,seconds,tabs,destinationIp) )
        t.daemon=True
        t.start()
        threads.append(t)
        
    # Rejoin the threads
    for t in threads:
        t.join()
        
    # Empty queue into whatever, probably a file
    while not queue.empty():  
        # Print function replace in not a template
        x1 =  queue.get()

    print "DONE" 
    time2 = time.time()
    print "Time to run complete request:  " + str(time2 - time1) ### make point to gui


def main():
	destinationIp = "1.1.1.1"
	seconds = "10"
	threadNumber = 50
	seed = "172.31.217.136"
	username = "admin"
	password = "cisco123"
	devicesList = info_crawl(seed,username,password)	
	threadwrapper = threadWrapper(devicesList,seconds,destinationIp,threadNumber)
	print "DONE FINAL!!!!"

if __name__ == '__main__':
	main()


#" monitor session 30 type erspan-source ; description ERSPAN30 for TEST ; source interface " + sourceInt + " both ; destination ip " + ip + " ; erspan-id 30 ; ip ttl 64 ; ip prec 0 ; ip dscp 0 ; mtu 1500 ; header-type 2 ; no shut ;"
#"monitor session 30 type erspan-destination ; description ERSPAN to 30 to POC ; erspan-id 30 ; vrf " + VVRFNAME +  " ; source ip " + IP + " ; destination "  +  DES  + " ; no shut ;"

# can fix not beaing able to stop look py only interating interface once, going back to the threading loop, then redoing it till you see an interrupt








# h