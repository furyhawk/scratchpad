const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>

<head>
    <title>GIMBAL_BASE_WEB</title>
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <!-- <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script> -->
    <style type="text/css">
    html {
        display: inline-block;
        text-align: center;
        font-family: sans-serif;
    }
    body {
        background-image: -webkit-linear-gradient(#3F424F, #1E212E);
        font-family: "roboto",helt "sans-serif";
        font-weight: lighter;
        background-position: center 0;
        background-attachment: fixed;
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
    }
    .cc-btn {
        border: 0;
        cursor: pointer;
        color: #fff;
        background: rgba(164,169,186,0);
        font-size: 1em;
        width: 100px;
        height: 100px;
         -webkit-touch-callout: none;
        -webkit-user-select: none;
        -khtml-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none; 
    }
    .cc-middle{
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: rgba(94,98,112,0.8);
    }
    .cc-btn:hover svg, .cc-middle:hover {
        opacity: 0.5;
    }
    .cc-btn:active svg, .cc-middle:hover{
        opacity: 0.5;
    }
    .controlor-c > div{
        width: 300px;
        height: 300px; 
        background-color: rgba(94,98,112,0.2);
        border-radius: 40px;
        box-shadow: 10px 10px 10px rgba(0,0,0,0.05);
        margin: auto;
    }
    .controlor-c > div > div{
        display: flex;
    }
    main {
        width: 960px;
        margin: auto;
    }
    section{margin: 40px 0;}
    .for-move {
        display: flex;
        align-items: center;
    }
    .for-move-a, .for-move-b{
        flex: 1;
        margin: 0 20px;
    }
    .h2-tt {
        font-size: 2em;
        font-weight: normal;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
    }
    .info-device-box .info-box{display: flex;}
    .info-device-box .info-box{padding: 20px 0;}
    .num-box-big > div, .num-box-sma > div{flex: 1;}
    .num-box-big > div:first-child{border-right: 1px solid rgba(216,216,216,0.1);}
    .num-box-mid {
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .num-box-mid div{
        width:33.3333%;
        margin: 20px 0;
    }
    .info-device-box .info-box > div > span {
        display: block;
    }
    .info-box {
        background-image: linear-gradient(to right, rgba(94, 98, 112, 0.3), rgba(75, 80, 95, 0.3)) ;
        margin: 20px auto;
        border: 1px solid rgba(216, 216, 216, 0.1);
        box-shadow: 10px 10px 10px rgba(0,0,0,0.05);
        border-radius: 4px;
        color: rgba(255,255,255,0.5);
    }
    .big-num{font-size: 3em;}
    .mid-num{font-size: 2em;}
    .sma-num{font-size: 1.2em;}
    .num-color{
        background-image: linear-gradient(rgba(255,255,255,1),rgba(255,255,255,0.5));
        background-clip: text;
        color:transparent;
        -webkit-background-clip: text;
        -moz-background-clip: text;
        -ms-background-clip: text;
        font-weight: 900;
        line-height: 1em;
        margin: 0.5em 0;
    }
    .num-color-red{
        background-image: linear-gradient(rgba(181,104,108,1),rgba(181,104,108,0.5));
        background-clip: text;
        color:transparent;
        -webkit-background-clip: text;
        -moz-background-clip: text;
        -ms-background-clip: text;
        font-weight: 900;
        line-height: 1em;
        margin: 0.5em 0;
    }
    .controlor > div {margin: 80px 0;}
    .json-cmd-info{
        display: flex;
        flex-wrap: wrap;
    }
    .json-cmd-info > div {
        width: 33.33333%;
        padding: 10px 0;
    }
    .json-cmd-info p{
        line-height: 30px;
        margin: 0;
    }
    .json-cmd-info p span {
        display: block;
        color: rgba(255,255,255,0.8);
    }
    .small-btn{
        color: rgba(255,255,255,0.8);
        background-color: #5E6270;
        border: none;
        height: 38px;
        border-radius: 4px;
    }
    .small-btn-active{
        background-color: rgba(38,152,234,0.1);
        color: #2698EA;
        border: 1px solid #2698EA;
        height: 38px;
        border-radius: 4px;
    }
    .feedb-p input{
        width: 100%;
        height: 46px;
        background-color: rgba(0,0,0,0);
        padding: 0 10px;
        border: 1px solid rgba(194,196,201,0.15);
        border-radius: 4px;
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.2em;
        margin-right: 10px;
    }
    .control-speed > div {
        width: 290px;
        margin: auto;
    }
    .control-speed > div > div{display: flex;}
    .control-speed label {flex: 1;}
    .small-btn, .small-btn-active{
        width: 90px;
    }
    .feedb-p{ display: flex;}
    .fb-input-info{
        margin: 0 20px;
    }
    .fb-info {margin: 20px;}
    .fb-info > span{line-height: 2.4em;}
    .btn-send:hover, .small-btn:hover{background-color: #2698EA;}
    .btn-send:active, .small-btn:active{background-color: #1b87d4;}
    .w-btn{
        color: #2698EA;
        background: transparent;
        padding: 10px;
        border: none;
    }
    .w-btn:hover{color: #2698EA;}
    .w-btn:active{color: #1b87d4;}
    @media screen and (min-width: 768px) and (max-width: 1200px){
        body{font-size: 16px;}
        main {
            width: 100%;
        }
        .for-move {
            display: block;
        }
        /* .controlor-c > div{width: 600px;height: 600px;}
        .cc-btn{width: 200px;height: 200px;} */
        .json-cmd-info{display: block;}
        .json-cmd-info p span{display: inline;}
        .json-cmd-info > div{
            display: flex;
            width: auto;
            padding: 20px;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        .control-speed > div{width: 600px;}
        section{margin: 20px 0;}
    }
    @media screen and (min-width: 360px) and (max-width: 767px){
        main {
            width: 100%;
        }
        .for-move {
            display: block;
        }
        .json-cmd-info{display: block;}
        .json-cmd-info p span{display: inline;}
        .json-cmd-info > div{
            display: flex;
            width: auto;
            padding: 20px;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        section{margin: 10px 0;}
        .info-box{margin: 10px auto;}
        .info-device-box .info-box{padding: 10px;}
        .num-box-mid div{margin: 10px 0;}
        .controlor-c > div{
            width: 270px;
            height: 270px;
        }
        .cc-btn{
            width: 90px;
            height: 90px;;
        }
        .big-num{font-size: 2em;}
        .controlor > div{margin: 40px 0;}
    }
    </style>
</head>
<body>
    <main>
        <section>
            <div>
                <h2 class="h2-tt" id="deviceInfo">Control Panel</h2>
            </div>
            <div class="for-move">
                <div class="for-move-a">
                    <div class="info-device-box">
                        <div class="info-box num-box-big">
                            <div >
                                <span class="big-num num-color" id="V">-1.01</span>
                                <span id="Vn">VOLTAGE</span>
                            </div>
                            <div>
                                <span class="big-num num-color" id="RSSI">-1.01</span>
                                <span id="RSSIn">RSSI</span>
                            </div>
                        </div>
                    </div>
                    <div class="info-device-box">
                        <div class="info-box num-box-sma">
                            <div>
                                <span class="num-color sma-num" id="IP">192.168.10.67</span>
                                <span id="IPn">IP</span>
                            </div>
                            <div>
                                <span class="num-color sma-num" id="MAC">44:17:93:EE:F8:F8</span>
                                <span id="MACn">MAC</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="for-move-b controlor">
                    <div class="controlor-c">
                        <div>
                            <div>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,-1,1);" ontouchstart="cmdSend(1,-1,1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="23" height="23" viewBox="0 0 23 23"><g style="mix-blend-mode:passthrough"><path d="M0,2L0,18.1716C0,19.9534,2.15428,20.8457,3.41421,19.5858L19.5858,3.41421C20.8457,2.15428,19.9534,0,18.1716,0L2,0C0.895431,0,0,0.895431,0,2Z" fill="#D8D8D8" fill-opacity="0.20000000298023224"/></g></svg></button></label>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,0,1);" ontouchstart="cmdSend(1,0,1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="26.87807685863504" height="15.435028109846826" viewBox="0 0 26.87807685863504 15.435028109846826"><g style="mix-blend-mode:passthrough" transform="matrix(0.9999999403953552,0,0,0.9999999403953552,0,0)"><path d="M12.0248,0.585787L0.589796,12.0208C-0.670133,13.2807,0.222199,15.435,2.00401,15.435L24.8741,15.435C26.6559,15.435,27.5482,13.2807,26.2883,12.0208L14.8533,0.585787C14.0722,-0.195262,12.8059,-0.195262,12.0248,0.585787Z" fill="#D8D8D8" fill-opacity="0.800000011920929"/></g></svg></button></label>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,1,1);" ontouchstart="cmdSend(1,1,1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="23" height="23" viewBox="0 0 23 23"><g style="mix-blend-mode:passthrough" transform="matrix(0,1,-1,0,23,-23)"><path d="M23,2L23,18.1716C23,19.9534,25.15428,20.8457,26.41421,19.5858L42.5858,3.41421C43.8457,2.15428,42.9534,0,41.1716,0L25,0C23.895431,0,23,0.895431,23,2Z" fill="#D8D8D8" fill-opacity="0.20000000298023224"/></g></svg></button></label>
                            </div>
                            <div>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,-1,0);" ontouchstart="cmdSend(1,-1,0);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="15.435028109846769" height="26.87807685863504" viewBox="0 0 15.435028109846769 26.87807685863504"><g style="mix-blend-mode:passthrough" transform="matrix(0.9999999403953552,0,0,0.9999999403953552,0,0)"><path d="M0.585787,14.8533L12.0208,26.2883C13.2807,27.5482,15.435,26.6559,15.435,24.8741L15.435,2.00401C15.435,0.222199,13.2807,-0.670133,12.0208,0.589795L0.585787,12.0248C-0.195262,12.8059,-0.195262,14.0722,0.585787,14.8533Z" fill="#D8D8D8" fill-opacity="0.800000011920929"/></g></svg></button></label>
                                <label><button class="cc-btn cc-middle" onmousedown="cmdSend(1,2,2);" ontouchstart="cmdSend(1,2,2);" onmouseup="cmdSend(1,2,2);" ontouchend="cmdSend(1,2,2);">MIDDLE</button></label>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,1,0);" ontouchstart="cmdSend(1,1,0);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="15.435030017195288" height="26.87807685863504" viewBox="0 0 15.435030017195288 26.87807685863504"><g style="mix-blend-mode:passthrough" transform="matrix(0.9999999403953552,0,0,0.9999999403953552,0,0)"><path d="M14.8492,12.0248L3.41422,0.589796C2.15429,-0.670133,-9.53674e-7,0.222199,9.53674e-7,2.00401L9.53674e-7,24.8741C-9.53674e-7,26.6559,2.15429,27.5482,3.41421,26.2883L14.8492,14.8533C15.6303,14.0722,15.6303,12.8059,14.8492,12.0248Z" fill="#D8D8D8" fill-opacity="0.800000011920929"/></g></svg></button></label>
                            </div>
                            <div>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,-1,-1);" ontouchstart="cmdSend(1,-1,-1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="23" height="23" viewBox="0 0 23 23"><g style="mix-blend-mode:passthrough" transform="matrix(0,-1,1,0,-23,23)"><path d="M0,25L0,41.1716C0,42.9534,2.15428,43.8457,3.41421,42.5858L19.5858,26.41421C20.8457,25.15428,19.9534,23,18.1716,23L2,23C0.895431,23,0,23.895431,0,25Z" fill="#D8D8D8" fill-opacity="0.20000000298023224"/></g></svg></button></label>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,0,-1);" ontouchstart="cmdSend(1,0,-1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="26.87807685863504" height="15.435030017195231" viewBox="0 0 26.87807685863504 15.435030017195231"><g style="mix-blend-mode:passthrough" transform="matrix(0.9999999403953552,0,0,0.9999999403953552,0,0)"><path d="M14.8533,14.8492L26.2883,3.41422C27.5482,2.15429,26.6559,-9.53674e-7,24.8741,9.53674e-7L2.00401,9.53674e-7C0.222199,-9.53674e-7,-0.670133,2.15429,0.589795,3.41421L12.0248,14.8492C12.8059,15.6303,14.0722,15.6303,14.8533,14.8492Z" fill="#D8D8D8" fill-opacity="0.800000011920929"/></g></svg></button></label>
                                <label><button class="cc-btn" onmousedown="cmdSend(1,1,-1);" ontouchstart="cmdSend(1,1,-1);" onmouseup="cmdSend(1,0,0);" ontouchend="cmdSend(1,0,0);"><svg fill="none" version="1.1" width="23" height="23" viewBox="0 0 23 23"><g style="mix-blend-mode:passthrough" transform="matrix(-1,0,0,-1,46,46)"><path d="M23,25L23,41.1716C23,42.9534,25.15428,43.8457,26.41421,42.5858L42.5858,26.41421C43.8457,25.15428,42.9534,23,41.1716,23L25,23C23.895431,23,23,23.895431,23,25Z" fill="#D8D8D8" fill-opacity="0.20000000298023224"/></g></svg></button></label>
                            </div>
                        </div>
                    </div>
                    <div class="control-speed">
                        <div>
                            <div id="device-speed-btn">
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(2,0,0);">TORQUE</button></label>
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(2,1,2);">P SET</button></label>
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(2,1,1);">T SET</button></label>
                            </div>
                        </div>
                        <div>
                            <div id="device-speed-btn">
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(3,0,0);">LED-OFF</button></label>
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(3,1,0);">LED-ON1</button></label>
                                <label><button name="speedbtn" class="small-btn" onclick="cmdSend(3,2,0);">LED-ON2</button></label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <section>
            <div class="fb-info">
                <h2 class="h2-tt" id="deviceInfo">Feedback infomation</h2>
                <span id="fbInfo" word-wrap="break-all">Json feedback infomation shows here.</span>
            </div>
            <div class="fb-input-info">
                <div class="feedb-p">
                    <input type="text" id="jsonData" placeholder="Input json cmd here.">
                    <label><button class="small-btn btn-send" onclick="jsonSend();">SEND</button></label>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>EMERGENCY_STOP: <span id="cmd0" class="cmd-value">{"T":0}</span> </p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd0');">INPUT</button>
                    </div>
                    <div>
                        <p>GIMBAL_CTRL: <span id="cmd1" class="cmd-value">{"T":1,"X":45,"Y":45,"SPD":0,"ACC":0}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd1');">INPUT</button>
                    </div>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>OLED_SET: <span id="cmd3" class="cmd-value">{"T":3,"lineNum":0,"Text":"putYourTextHere"}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd3');">INPUT</button>
                    </div>
                    <div>
                        <p>OLED_DEFAULT: <span id="cmd-3" class="cmd-value">{"T":-3}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd-3');">INPUT</button>
                    </div>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>ALL_LIGHT_OFF: <span id="cmd4" class="cmd-value">{"T":41, "SA":0, "SB":0}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd4');">INPUT</button>
                    </div>
                    <div>
                        <p>LIGHT_PWM_CTRL: <span id="cmd-4" class="cmd-value">{"T":41, "SA":255, "SB":255}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd-4');">INPUT</button>
                    </div>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>BUS_SERVO_CTRL: <span id="cmd50" class="cmd-value">{"T":50,"id":1,"pos":2047,"spd":500,"acc":30}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd50');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_MID: <span id="cmd-5" class="cmd-value">{"T":-5,"id":1}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd-5');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_SCAN: <span id="cmd52" class="cmd-value">{"T":52,"num":20}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd52');">INPUT</button>
                    </div>

                    <div>
                        <p>BUS_SERVO_INFO: <span id="cmd53" class="cmd-value">{"T":53,"id":1}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd53');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_ID_SET: <span id="cmd54" class="cmd-value">{"T":54,"old":1,"new":2}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd54');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_TORQUE_LOCK: <span id="cmd55" class="cmd-value">{"T":55,"id":1,"status":1}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd55');">INPUT</button>
                    </div>

                    <div>
                        <p>BUS_SERVO_TORQUE_LIMIT: <span id="cmd56" class="cmd-value">{"T":56,"id":1,"limit":500}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd56');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_MODE: <span id="cmd57" class="cmd-value">{"T":57,"id":1,"mode":0}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd57');">INPUT</button>
                    </div>
                    <div>
                        <p>BUS_SERVO_MID_SET: <span id="cmd57" class="cmd-value">{"T":58,"id":1}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd57');">INPUT</button>
                    </div>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>WIFI_INFO: <span id="cmd65" class="cmd-value">{"T":65}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd65');">INPUT</button>
                    </div>
                </div>
                <div class="info-box json-cmd-info">
                    <div>
                        <p>INA219_INFO: <span id="cmd70" class="cmd-value">{"T":70}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd70');">INPUT</button>
                    </div>
                    <div>
                        <p>IMU_INFO: <span id="cmd71" class="cmd-value">{"T":71}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd71');">INPUT</button>
                    </div>
                    <div>
                        <p>DEVICE_INFO: <span id="cmd74" class="cmd-value">{"T":74}</span></p>
                        <button class="w-btn" onclick="cmdFill('jsonData', 'cmd74');">INPUT</button>
                    </div>
                </div>
            </div>
        </section>
    </main>
<script>
    setInterval(function() {
        infoUpdate();
    }, 458);

    function cmdFill(rawInfo, fillInfo) {
        document.getElementById(rawInfo).value = document.getElementById(fillInfo).innerHTML;
    }
    function jsonSendFb() {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
              document.getElementById("fbInfo").innerHTML =
              this.responseText;
            }
        };
        xhttp.open("GET", "jsfb", true);
        xhttp.send();
    }
    function jsonSend() {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "js?json="+document.getElementById('jsonData').value, true);
        xhttp.send();
        jsonSendFb();
    }
    function infoUpdate() {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var jsonResponse = JSON.parse(this.responseText);
                document.getElementById("V").innerHTML = jsonResponse.V;
                if (jsonResponse.V<11.06) {
                    document.getElementById("V").classList.remove("num-color");
                    document.getElementById("V").classList.add("num-color-red");
                }else{
                    document.getElementById("V").classList.remove("num-color-red");
                    document.getElementById("V").classList.add("num-color");
                }

                document.getElementById("r").innerHTML = jsonResponse.r;
                document.getElementById("p").innerHTML = jsonResponse.p;
                document.getElementById("y").innerHTML = jsonResponse.y;

                document.getElementById("mX").innerHTML = jsonResponse.mX;
                document.getElementById("mY").innerHTML = jsonResponse.mY;
                document.getElementById("mZ").innerHTML = jsonResponse.mZ;

                document.getElementById("IP").innerHTML = jsonResponse.IP;
                document.getElementById("MAC").innerHTML = jsonResponse.MAC;
                document.getElementById("RSSI").innerHTML = jsonResponse.RSSI;
            }
        };
        xhttp.open("GET", "deviceInfo", true);
        xhttp.send();

    }

    function cmdSend(inputA, inputB, inputC){
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "cmd?inputA="+inputA+"&inputB="+inputB+"&inputC="+inputC, true);
        xhr.send();
    }
</script>
</body>
</html>
)rawliteral";