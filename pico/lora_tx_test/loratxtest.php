<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
<meta charset="utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
<meta name="viewport" content="initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>lora tx test</title>
<meta name="keywords" content="" />
<meta name="description" content="" />

<script src="js/jquery-1.7.2.min.js"></script>
<script type="text/javascript">
var blestart=0;
var showmpass=0;
var xmlHttp;
var checkhex="\"this.value=this.value.replace(/[^0-9a-fA-F]/g,'');\"";
var checkdec="\"this.value=this.value.replace(/[^0-9]/g,'');\"";
function createXMLHttpRequest(){
	if(window.ActiveXObject){
		xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	else if(window.XMLHttpRequest){
		xmlHttp = new XMLHttpRequest();
	}
}

function post(url,para,Func){
	createXMLHttpRequest();
	xmlHttp.open("POST",url,true);
	xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState === 4 && xmlHttp.status === 200){            
		//console.log(xmlHttp.responseText);
			var result=JSON.parse(xmlHttp.responseText);
			Func(result);
		}
	}
	xmlHttp.setRequestHeader("Content-type", "application/json");
	xmlHttp.send(para);
}
function loratest(){
	var para = new Object();
	para.apply="txtest";
	para.region=$('#region').val();
	console.log(JSON.stringify(para));
	post('txtest.php',JSON.stringify(para),loratest_callback);
}
function loratest_callback(status)
{
	alert("Tx started!");
}
</script>
</head>
<body>
</select>
<select id="region" style="width:200px; margin-bottom:10px">
  <option value ="US915">US915</option>
  <option value ="AS923_1">AS923_1</option>
  <option value ="AS923_2">AS923_2</option>
  <option value ="EU868">EU868</option>
</select>
<button onClick='loratest()' style="width:100px; margin-bottom:10px">tx test</button>
</div>

</body>
</html>

