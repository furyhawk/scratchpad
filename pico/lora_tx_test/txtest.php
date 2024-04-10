<?php
$body = file_get_contents('php://input');

//echo $body;
$body=json_decode($body,true);

switch($body["apply"])
{
	case 'txtest':
		loratest($body);
		break;
	default:
		break;
}

function loratest($body)
{
	$cmd="sudo killall lora_test.sh";
	exec($cmd,$res);
	$cmd="sudo /root/lora_tx_test/lora_test.sh ".$body["region"]." > /dev/null &";
	exec($cmd,$res);
	echo "{}";
}

