# README #

Frankenrouter software defined networking for proxadmin

#
1. edit frankenrouter/config.sh to add the transport ips and the subnet mask
2. add to crontab:

* *     * * *   root    python3 /root/frankenrouter/updateipcache.py >> /root/ipstate.log
* *     * * *   root    sleep 30 ; python3 /root/frankenrouter/updateipcache.py >> /root/ipstate.log

### Tests ###

* SHOULD be able to ping your own pub ip
* SHOULD NOT be able to ping 10.0.102.10 (other client VDC)
* COULD be able to ping 10.0.102.1 (other clinet VDC router)
* SHOULD be able to ping other client public ip

