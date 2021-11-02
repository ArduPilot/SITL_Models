RealFlight panoramas to use with SITL.

For the ARP_SriptNZ fields, one has the plane spawn for north takeoff, and the other for south. Helicopter spawn is in the same location for both. They include collisoion data, so be careful on takeoff and landing :-)
SITL should be started with this location data, depending on the takeoff direction (can be added to the locations.txt file).
ARPstrip_NZ_S=-43.6541316, 172.5029844,0,156  #Strip in New Zealand, South takeoff
ARPstrip_NZ_N=-43.6545022, 172.5031883,0,336  #Strip in New Zealand, North takeoff