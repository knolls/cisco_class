Cdp_Crawler will crawl all the device build objects that contain info about the crawled device then returns a list of these objects.

AutoShark Multi will crawl everything get the devices list,then monitor each device in its own thread. When it sees an interface with over 1000 packets (this is a place holder it would monitor errors) then it creates an acl to punt everything to the cpu and starts an etheranylizer. Its not very useful Multi spanner does a better job.

Multispanner will crawl everything get the devices list, then monitor each device in its own thread. When it sees an interface with over 1000 packets (this is a place holder it would monitor errors) then it will create an erspan session on that port for x amount of time. when the timer ends it will clean up the erspan session and continue to monitor the device
