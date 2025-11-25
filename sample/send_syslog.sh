#!/bin/bash
# send syslog via nc to a local fluent-bit listening on 514
SYSLOG_MSG="<134>Aug 20 12:44:56 fw01 vendor=demo product=ngfw action=deny src=10.0.1.10 dst=8.8.8.8 spt=5353 dpt=53 proto=udp msg=DNS blocked"


# adjust IP/PORT of collector
nc -u 127.0.0.1 514 <<< "$SYSLOG_MSG"