#! /bin/sh
rrdtool create temp-1-1.rrd --start 1386194444 --step 30 \
             DS:temp:GAUGE:300:-1.0000000000e+01:1.0000000000e+02 \
             RRA:AVERAGE:0.5:1:518400 \
             RRA:AVERAGE:0.5:10:207360 \
             RRA:AVERAGE:0.5:120:36000 \
             RRA:MAX:0.5:10:207360 \
             RRA:MIN:0.5:10:207360 \
             RRA:MAX:0.5:120:36000 \
             RRA:MIN:0.5:120:36000 
