#!/bin/bash

# tcp: 1 vehicle
mavproxy.py \
--out 127.0.0.1:14550 \
--out 127.0.0.1:14551 \
--master tcp:127.0.0.1:5760 \
--sitl 127.0.0.1:5501 \
\
--map \
--console

