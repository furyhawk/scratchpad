#!/bin/sh
region=$1
if [ "$region" = "US915" ]
then
	freq=903.9
elif [ "$region" = "AS923_1" ]
then
        freq=923.2
elif [ "$region" = "AS923_2" ]
then
        freq=921.4
elif [ "$region" = "EU868" ]
then
        freq=867.1
fi
cnt=20;
n=0
while [ "$n" != "$cnt" ]
do
tmp=`expr $n % 8`
tmp=$(echo "$freq+$tmp*0.2"|bc)
/root/lora_tx_test/test_loragw_hal_tx -d /dev/spidev32766.0 -r 1250 -m 'LORA' -b 125  -f $tmp  -s 9 -n 1 --pa 0 --pwid 17 -z 55
n=`expr $n + 1`;
sleep 3
done

systemctl restart lrgateway
