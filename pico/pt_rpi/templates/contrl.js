var robot_name, cmd_movition_ctrl, max_speed, slow_speed;
var cmd_gimbal_ctrl, cmd_gimbal_base_ctrl, cmd_gimbal_steady;
var max_rate, mid_rate, min_rate;
var max_res, mid_res, min_res; 
var zoom_x1, zoom_x2, zoom_x4;
var pic_cap, vid_sta, vid_end;
var mc_lock, mc_unlo;
var cv_none, cv_moti, cv_face, cv_objs, cv_clor, cv_hand, cv_auto;
var re_none, re_capt, re_reco, led_off, led_aut, led_ton, base_of, base_on;
var head_ct, base_ct;
var s_panid, release, set_mid, s_tilid;

var detect_type, led_mode, detect_react, picture_size, video_size, cpu_load;
var cpu_temp, ram_usage, pan_angle, tilt_angle, wifi_rssi, base_voltage, video_fps;
var cv_movtion_mode, base_light;

fetch('/config')
  .then(response => response.text())
  .then(yamlText => {
    try {
      const yamlObject = jsyaml.load(yamlText);
      console.log(yamlObject); // YAML 文件现在被转换成了 JavaScript 对象
      cmd_movition_ctrl = yamlObject.cmd_config.cmd_movition_ctrl;
      cmd_gimbal_steady = yamlObject.cmd_config.cmd_gimbal_steady;
      cmd_gimbal_ctrl = yamlObject.cmd_config.cmd_gimbal_ctrl;
      cmd_gimbal_base_ctrl = yamlObject.cmd_config.cmd_gimbal_base_ctrl;

      max_speed = yamlObject.args_config.max_speed;
      slow_speed = yamlObject.args_config.slow_speed;
      robot_name = yamlObject.base_config.robot_name;

      max_rate  = yamlObject.args_config.max_rate;
      mid_rate  = yamlObject.args_config.mid_rate;
      min_rate  = yamlObject.args_config.min_rate;

      max_res = yamlObject.code.max_res;
      mid_res = yamlObject.code.mid_res;
      min_res = yamlObject.code.min_res;

      zoom_x1 = yamlObject.code.zoom_x1;
      zoom_x2 = yamlObject.code.zoom_x2;
      zoom_x4 = yamlObject.code.zoom_x4;

      pic_cap = yamlObject.code.pic_cap;
      vid_sta = yamlObject.code.vid_sta;
      vid_end = yamlObject.code.vid_end;

      mc_lock = yamlObject.code.mc_lock;
      mc_unlo = yamlObject.code.mc_unlo;

      cv_none = yamlObject.code.cv_none;
      cv_moti = yamlObject.code.cv_moti;
      cv_face = yamlObject.code.cv_face;
      cv_objs = yamlObject.code.cv_objs;
      cv_clor = yamlObject.code.cv_clor;
      cv_hand = yamlObject.code.cv_hand;
      cv_auto = yamlObject.code.cv_auto;

      re_none = yamlObject.code.re_none;
      re_capt = yamlObject.code.re_capt;
      re_reco = yamlObject.code.re_reco;
      led_off = yamlObject.code.led_off;
      led_aut = yamlObject.code.led_aut;
      led_ton = yamlObject.code.led_ton;
      base_of = yamlObject.code.base_of;
      base_on = yamlObject.code.base_on;
      head_ct = yamlObject.code.head_ct;
      base_ct = yamlObject.code.base_ct;

      s_panid = yamlObject.code.s_panid;
      release = yamlObject.code.release;
      set_mid = yamlObject.code.set_mid;
      s_tilid = yamlObject.code.s_tilid;

      detect_type = yamlObject.fb.detect_type;
      led_mode    = yamlObject.fb.led_mode;
      detect_react= yamlObject.fb.detect_react;
      picture_size= yamlObject.fb.picture_size;
      video_size  = yamlObject.fb.video_size;
      cpu_load    = yamlObject.fb.cpu_load;
      cpu_temp    = yamlObject.fb.cpu_temp;
      ram_usage   = yamlObject.fb.ram_usage;
      pan_angle   = yamlObject.fb.pan_angle;
      tilt_angle  = yamlObject.fb.tilt_angle;
      wifi_rssi   = yamlObject.fb.wifi_rssi;
      base_voltage= yamlObject.fb.base_voltage;
      video_fps   = yamlObject.fb.video_fps;
      cv_movtion_mode = yamlObject.fb.cv_movtion_mode;
      base_light  = yamlObject.fb.base_light;

      if (robot_name) {
        document.title = robot_name + " WEB CTRL";
      }
    } catch (e) {
      console.error('Error parsing YAML file:', e);
    }
  })
  .catch(error => {
    console.error('Error fetching YAML file:', error);
  });

//update photos list
function generatePhotoLink(imgname) {
    var strippedname = imgname.replace("photo_", "").replace(".jpg", "");
    var photoLink = '<li><a target="_blank" href="./static/' + imgname + '" ><img class="photo_img" data-filename="' +imgname + '" src="./static/' + imgname + '" /></a>';
    photoLink += '<p>' + strippedname + '</p>';
    photoLink += '<div class="delete_btn"><button class="normal_btn delete_btn_size normal_btn_del btn_ico"></button></div></li>';
    return photoLink;
}
function updatePhotoNames() {
    $.get('/get_photo_names', function(data) {
        var photoLinks = '';
        if (window.location.pathname === '/') {
            for (var i = 0; i < 6; i++) {
                var name = data[i];
                photoLinks += generatePhotoLink(name);
            }
            $('#photo-list').html(photoLinks);
        } else {
            for (var i = 0; i < data.length; i++) {
                var name = data[i];
                photoLinks += generatePhotoLink(name);
            }
            $('#photo-list').html(photoLinks);
        }
        $("#number-photos").text(data.length);
        //delete photo
        $("#photo-list li button").on("click", function () {
        var filename = $(this).closest("li").find("img.photo_img").data('filename');
        $.post('/delete_photo', { filename: filename }, function(response) {
            if (response.success) {
                updatePhotoNames();
            } else {
                alert("Failed to delete the file.");
            }
        });
    });
    });
}
updatePhotoNames();
setInterval(updatePhotoNames, 2000);


//show videos tips
function showVideosTips(){
    var videostipsbox =  $("#video-del-tips");
    videostipsbox.css("opacity", "1");
    videostipsbox.css("transform", `translate(-50%, -100%)`);
    setTimeout(function() {
        videostipsbox.removeAttr("style");
    }, 2000);
}

//update videos list
function generateVideoLink(vname) {
    var strippedname = vname.replace("video_", "").replace(".mp4", "");
    var videoList = '<li><a target="_blank" data-filename="' + vname + '" href="./videos/' + vname +'">';
    videoList += '<p>' + strippedname + '</p>';
    videoList += '<div><div class="delete_btn_size normal_btn_play btn_ico"></div></div></a>';
    videoList += '<div class="delete_btn"><div class="delete_btn_size normal_btn_del btn_ico"></div></div></li>';
    return videoList;
}
function updateVideoList() {
    $.get('/get_video_names', function(data) {
        var videosLists = '';
        if (window.location.pathname === '/') {
            for (var i = 0; i < 6; i++) {
                var name = data[i];
                videosLists += generateVideoLink(name);
            }
            $('#video-list').html(videosLists);
        } else {
            for (var i = 0; i < data.length; i++) {
                var name = data[i];
                videosLists += generateVideoLink(name);
            }
            $('#video-list').html(videosLists);
        }
        $("#number-videos").text(data.length);
        //delete videos
        $("#video-list li div.normal_btn_del").on("click", function () {
        var filename = $(this).closest("li").find("a").data('filename');
        $.post('/delete_video', { filename: filename }, function(response) {
            if (response.success) {
                updateVideoList();
                showVideosTips();
            } else {
                alert("Failed to delete the video.");
                }
            });
        });
    });
}
updateVideoList();


//video pixel
var listItems = $("#video_pixel_btn_list").children("li");
listItems.on("click", function () {
    var innertext = $(this).text();
    $("#video_pixel_btn").text(innertext);
    $("#video_pixel_btn_list").css("display", "none");
    setTimeout(function () {
        $("#video_pixel_btn_list").removeAttr("style");
    }, 10);  
});

//record function
$(document).ready(function () {
    var isRecording = false;
    var originalText = "Record";
    var timerInterval;
    var seconds = 0;
    var minutes = 0;

    function updateTimer() {
        seconds++;
        if (seconds === 60) {
            seconds = 0;
            minutes++;
        }
        var formattedTime = (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
        $("#record-btn").text(formattedTime);
    }

    $("#record-btn").click(function () {
        if (!isRecording) {
            cmdSend(vid_sta,0,0);
            $(this).css("color", "#FF8C8C");
            $(this).removeClass("video_btn_record");
            $(this).addClass("video_btn_stop");
            isRecording = true;
            $(this).text("00:00");
            timerInterval = setInterval(updateTimer, 1000);
        } else {
            cmdSend(vid_end,0,0);
            $(this).removeClass("video_btn_stop");
            $(this).addClass("video_btn_record");
            $(this).text(originalText);
            isRecording = false;
            clearInterval(timerInterval);
            seconds = 0;
            minutes = 0;
            $(this).css("color", "");
            updateVideoList();
        }
    });
});

//zoom
var zoomx = 1;
$("#zoom_btn").click(function(){
    var zoomNum  = document.getElementById("zoom-num");
    switch(zoomx){
        case 0: cmdSend(zoom_x1,0,0);
        zoomNum.innerHTML = "1x" 
        break;
        case 1: cmdSend(zoom_x2,0,0);
        zoomNum.innerHTML = "2x" 
        break;
        case 2: cmdSend(zoom_x4,0,0);
        zoomNum.innerHTML = "4x" 
        break;
    }
    zoomx = (zoomx + 1) % 3;
});

//joy stick function
var largeCircle = $("#ctrl_base");
var smallCircle = $("#ctrl_base div");
var minifyTimeout;
var isEnlarged = false;
var isMouseUp = false;
function enlargeJoyStick(){
    setTimeout(() => {
        isEnlarged = true;
    }, 98);
    largeCircle.removeClass("ctrl_base_s");
    smallCircle.removeClass("ctrl_stick_s");
    largeCircle.addClass("ctrl_base_l");
    smallCircle.addClass("ctrl_stick_l");
}
function minifyJoyStick(){
    isEnlarged = false;
    isMouseUp = false;
    largeCircle.removeClass("ctrl_base_l");
    smallCircle.removeClass("ctrl_stick_l");
    largeCircle.addClass("ctrl_base_s");
    smallCircle.addClass("ctrl_stick_s");
    
}
largeCircle.on("click", function(e){
    clearTimeout(minifyTimeout);
    enlargeJoyStick();
});

largeCircle.on("mousedown touchstart", function(){
    isMouseUp = false;
    clearTimeout(minifyTimeout);
    enlargeJoyStick();
});
$(document).on("mouseup touchend", function(){
    isMouseUp = true;
    if (isEnlarged) {
        minifyTimeout = setTimeout(minifyJoyStick, 2000);
    }
});
largeCircle.on("mouseenter", function(){
    clearTimeout(minifyTimeout);
});
largeCircle.on("mouseleave", function() {
    if (isMouseUp && isEnlarged) {
        minifyTimeout = setTimeout(minifyJoyStick, 2000);
    }
});


const base = document.getElementById('ctrl_base');
const stick = document.getElementById('ctrl_stick');
let isDragging = false;
let stickStartX = 0;
let stickStartY = 0;

var stickSendX = 0;
var stickSendY = 0;

var stickLastX = 0;
var stickLastY = 0;
// JoyStick actions for pc
try {
    stick.addEventListener('mousedown', (e) => {
        isDragging = true;
        stick.style.transition = 'none';
        const stickRect = stick.getBoundingClientRect();
        stickStartX = e.clientX - stickRect.left - stickRect.width / 2;
        stickStartY = e.clientY - stickRect.top - stickRect.height / 2;
        stickLastX = stickSendX;
        stickLastY = stickSendY;
    });
} catch(e) {
    console.log(e);
}
document.addEventListener('mousemove', (e) => {
    if (isDragging && isEnlarged) {
        moveStick(e);
    }
});
document.addEventListener('mouseup', () => {
    isDragging = false;
    try {
        stick.style.transition = '0.3s ease-out';
        stick.style.transform = 'translate(-50%, -50%)';
        base.style.border = '';
    } catch(e) {
        console.log(e);
    }
});
// JoyStick actions for mobile devices
try {
    stick.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isDragging = true;
        stick.style.transition = 'none';
        const touch = e.touches[0];
        const stickRect = stick.getBoundingClientRect();
        stickStartX = touch.clientX - stickRect.left - stickRect.width / 2;
        stickStartY = touch.clientY - stickRect.top - stickRect.height / 2;
        stickLastX = stickSendX;
        stickLastY = stickSendY;
    });
} catch(e) {
    console.log(e);
}
document.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (isDragging && isEnlarged) {
        const touch = e.touches[0];
        moveStick(touch);
    }
});
try {
    stick.addEventListener('touchend', (e) => {
        //e.preventDefault();
        isDragging = false;
        stick.style.transition = '0.3s ease-out';
        stick.style.transform = 'translate(-50%, -50%)';
        base.style.border = '';
    });
} catch(e) {
    console.log(e);
}
function moveStick(event) {
    const baseRect = base.getBoundingClientRect();
    const stickRect = stick.getBoundingClientRect();
    const baseRectHalfW = baseRect.width / 2;
    const baseRectHalfH = baseRect.height / 2;

    const centerX = baseRect.left + baseRectHalfW;
    const centerY = baseRect.top + baseRectHalfH;

    const deltaX = event.clientX - centerX - stickStartX;
    const deltaY = event.clientY - centerY - stickStartY;

    const distance = Math.min(baseRectHalfW, Math.sqrt(deltaX ** 2 + deltaY ** 2));
    const angle = Math.atan2(deltaY, deltaX);

    const stickX = centerX + distance * Math.cos(angle);
    const stickY = centerY + distance * Math.sin(angle);

    const stickmovex = stickX - centerX - stickRect.width /2;
    const stickmovey = stickY - centerY - stickRect.height /2;

    stick.style.transform = `translate(${stickmovex}px, ${stickmovey}px)`;

    if (distance == baseRect.width / 2) {
        base.style.border = '2px solid #4FF5C0';
    } else {
        base.style.border = '';
    }

    stickSendX = stickLastX + deltaX;
    stickSendY = stickLastY + deltaY;

    joyStickCtrl(stickSendX, stickSendY);
}


function joyStickCtrl(inputX, inputY) {
    var x_cmd = Math.max(-180, Math.min(inputX/2.5, 180));
    var y_cmd = Math.max(-45, Math.min(-inputY/2.5, 90));

    cmdJsonCmd({"T":cmd_gimbal_ctrl,"X":inputX/2.5,"Y":-inputY/2.5,"SPD":0,"ACC":128});


    RotateAngle = document.getElementById("Pan").innerHTML = x_cmd.toFixed(2);
    var panScale = document.getElementById("pan_scale");
    panScale.style.transform = `rotate(${-RotateAngle}deg)`;

    var tiltNum = document.getElementById("Tilt");
    var tiltNumPanel = tiltNum.getBoundingClientRect();
    var tiltNumMove = tiltNum.innerHTML = y_cmd.toFixed(2);;

    var pointer = document.getElementById('tilt_scale_pointer');
    var tiltScaleOut = document.getElementById('tilt_scale');
    var tiltScaleBase = tiltScaleOut.getBoundingClientRect();
    var tiltScalediv = document.getElementById('tilt_scalediv');
    var tiltScaleDivBase = tiltScalediv.getBoundingClientRect();
    var pointerMoveY = tiltScaleBase.height/135;
    pointer.style.transform = `translate(${tiltScaleDivBase.width}px, ${pointerMoveY*(90 - tiltNumMove)-tiltNumPanel.height/2}px)`;
}


//seetting page
function confirmSetPanID() {
    if (confirm("Make sure that you have already DISCONNECT the wire of the Tilt Servo")) {
        cmdSend(s_panid, 0, 0);
    }
}
function confirmRelease() {
    if (confirm("You will unlock the torque lock, then you can manually adjust the angle of the two servos.")) {
        cmdSend(release, 0, 0);
    }
}
function confirmMiddleSet() {
    if (confirm("Set the current position as the middle position.")) {
        cmdSend(set_mid, 0, 0);
    }
}
function confirmSetTiltID() {
    if (confirm("If you didn't disconnect the Tilt Servo in step 1, then both servo IDs will be set to 2 after you click the [Set Pan ID] button. Only in this case, you need to click [Set Tilt ID] to restore both servo IDs to 1, then repeat the entire setup process!")) {
        cmdSend(s_tilid, 0, 0);
    }
}




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


//remove buttons class
function removeButtonsClass(buttons) {
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove("ctl_btn_active");
    }
}
//remove all ico class
function removeAllIcoClass(ElName){
    while (ElName.classList.length > 0) {
        ElName.classList.remove(ElName.classList.item(0));
    }
}

var socketJson = io('http://' + location.host + '/json');
socketJson.emit('json', {'T':1,'L':0,'R':0})

var socket = io('http://' + location.host + '/ctrl');
socket.emit('request_data');

var light_mode = 0;
socket.on('update', function(data) {
    if (data[base_voltage] != 0) {
        // console.log(data[detect_react]);
    } else {
        return;
    }
    try {
        var dtIco = document.getElementById("DT");
        var dTypeBtn = document.getElementById("d_type_btn");
        var DTbuttons = dTypeBtn.getElementsByTagName("button");
        removeAllIcoClass(dtIco);
        removeButtonsClass(DTbuttons);
        if (data[detect_type] == cv_none) {
            dtIco.classList.add("feed_ico", "feed_ico_none");
            DTbuttons[0].classList.add("ctl_btn_active");
        } else if (data[detect_type] == cv_moti) {
            dtIco.classList.add("feed_ico", "feed_ico_movtion");
            DTbuttons[1].classList.add("ctl_btn_active");
        } else if (data[detect_type] == cv_face) {
            dtIco.classList.add("feed_ico", "feed_ico_face");
            DTbuttons[2].classList.add("ctl_btn_active");
        }

        var drIco = document.getElementById("DR");
        var DReactionBtn = document.getElementById("d_reaction_btn");
        var DRbuttons = DReactionBtn.getElementsByTagName("button");
        removeButtonsClass(DRbuttons);
        if (data[detect_react] == re_none) {
            removeAllIcoClass(drIco);
            drIco.classList.add("feed_ico", "feed_ico_none");
            DRbuttons[0].classList.add("ctl_btn_active");
        } else if (data[detect_react] == re_capt) {
            removeAllIcoClass(drIco);
            drIco.classList.add("feed_ico", "feed_ico_capture");
            DRbuttons[1].classList.add("ctl_btn_active");
        } else if (data[detect_react] == re_reco) {
            removeAllIcoClass(drIco);
            drIco.classList.add("feed_ico", "feed_ico_record");
            DRbuttons[2].classList.add("ctl_btn_active");
        }

        lightMode = document.getElementById("MODE");
        var lightCtrlBtn = document.getElementById("light_ctrl_btn");
        var lbuttons = lightCtrlBtn.getElementsByTagName("button");
        removeButtonsClass(lbuttons);
        light_mode = data[led_mode];
        if (data[led_mode] == 0) {
            lightMode.innerHTML = "OFF";
            lbuttons[0].classList.add("ctl_btn_active");
        } else if (data[led_mode] == 1) {
            lightMode.innerHTML = "AUTO";
            lbuttons[1].classList.add("ctl_btn_active");
        } else if (data[led_mode] == 2) {
            lightMode.innerHTML = "ON";
            lbuttons[2].classList.add("ctl_btn_active");
        }

        document.getElementById("CPU").innerHTML = data[cpu_load] + "%";
        document.getElementById("tem").innerHTML = data[cpu_temp].toFixed(1) + " ℃";
        document.getElementById("RAM").innerHTML = data[ram_usage] + "%";
        document.getElementById("rssi").innerHTML = data[wifi_rssi] + " dBm";
        document.getElementById("fps").innerHTML = data[video_fps].toFixed(1);
        
        document.getElementById("photos-size").innerHTML = data[picture_size] + " MB";
        document.getElementById("videos-size").innerHTML = data[video_size] + " MB";

        document.getElementById("v_in").innerHTML = data[base_voltage].toFixed(1);
        
        var element = document.getElementById("b_state");
        element.classList.remove("baterry_state", "baterry_state1", "baterry_state2", "baterry_state3");
        if (data[base_voltage] >= 10.5) {
            element.classList.add("baterry_state");
        } else if (data[base_voltage] >= 10) {
            element.classList.add("baterry_state","baterry_state3");
        } else if (data[base_voltage] >= 9.5) {
            element.classList.add("baterry_state","baterry_state2");
        } else if (data[base_voltage] < 9.5) {
            element.classList.add("baterry_state","baterry_state1");
        }
    } catch(e) {
        console.log(e);
    }

});

var heartbeat_left  = 0;
var heartbeat_right = 0;
var speed_rate = 0.3;
var defaultSpeed = speed_rate;
function cmdSend(inputA, inputB, inputC){
    var jsonData = {
        "A":inputA,
        "B":inputB,
        "C":inputC
    };
    console.log(jsonData);
    socket.send(JSON.stringify(jsonData));
}

function cmdJsonCmd(jsonData){
    console.log(jsonData);
    // if (jsonData.T == cmd_movition_ctrl) {
    //     heartbeat_left = jsonData.L;
    //     heartbeat_right = jsonData.R;
    //     jsonData.L = heartbeat_left * speed_rate;
    //     jsonData.R = heartbeat_right * speed_rate;
    // }
    socketJson.emit('json', jsonData);
}

// var moveKeyMap = {
//     16: 'shift', // acce
//     49: 'low',
//     50: 'middle',
//     51: 'fast',
//     65: 'left',   // A
//     87: 'forward', // W
//     83: 'backward', // S
//     68: 'right', // D
// }
// var move_buttons = {
//     shift: 0,
//     low: 0,
//     middle: 0,
//     fast: 0,
//     forward: 0,
//     backward: 0,
//     left: 0,
//     right: 0,
// }
// function moveProcess() {
//     var forwardButton  = move_buttons.forward;
//     var backwardButton = move_buttons.backward;
//     var leftButton  = move_buttons.left;
//     var rightButton = move_buttons.right;

//     // Speed Ctrl
//     if (move_buttons.low == 1){
//         speedCtrl(min_rate);
//     } else if (move_buttons.middle == 1){
//         speedCtrl(mid_rate);
//     } else if (move_buttons.fast == 1){
//         speedCtrl(max_rate);
//     }

//     if(move_buttons.shift == 1) {
//         speed_rate = max_rate;
//         var spdCtrlBtn = document.getElementById("speed_ctrl_btn");
//         var spdbuttons = spdCtrlBtn.getElementsByTagName("button");
//         removeButtonsClass(spdbuttons);
//         if (speed_rate <= 0.33) {
//             spdbuttons[0].classList.add("ctl_btn_active");
//         } else if (speed_rate > 0.33 && speed_rate < 0.66) {
//             spdbuttons[1].classList.add("ctl_btn_active");
//         } else if (speed_rate >= 0.66) {
//             spdbuttons[2].classList.add("ctl_btn_active");
//         }
//     } else {
//         speedCtrl(defaultSpeed);
//     }

//     // Movtion Ctrl
//     if (forwardButton == 0 && backwardButton == 0 && leftButton == 0 && rightButton == 0) {
//         heartbeat_left  =  0;
//         heartbeat_right =  0;
//     }else if (forwardButton == 1 && backwardButton == 0 && leftButton == 0 && rightButton == 0){
//         heartbeat_left  =  max_speed;
//         heartbeat_right =  max_speed;
//     }else if (forwardButton == 0 && backwardButton == 1 && leftButton == 0 && rightButton == 0){
//         heartbeat_left  = -max_speed;
//         heartbeat_right = -max_speed;
//     }else if (forwardButton == 0 && backwardButton == 0 && leftButton == 1 && rightButton == 0){
//         heartbeat_left  = -max_speed;
//         heartbeat_right =  max_speed;
//     }else if (forwardButton == 0 && backwardButton == 0 && leftButton == 0 && rightButton == 1){
//         heartbeat_left  =  max_speed;
//         heartbeat_right = -max_speed;
//     }else if (forwardButton == 1 && backwardButton == 0 && leftButton == 1 && rightButton == 0){
//         heartbeat_left  =  slow_speed;
//         heartbeat_right =  max_speed;
//     }else if (forwardButton == 1 && backwardButton == 0 && leftButton == 0 && rightButton == 1){
//         heartbeat_left  =  max_speed;
//         heartbeat_right =  slow_speed;
//     }else if (forwardButton == 0 && backwardButton == 1 && leftButton == 1 && rightButton == 0){
//         heartbeat_left  = -slow_speed;
//         heartbeat_right = -max_speed;
//     }else if (forwardButton == 0 && backwardButton == 1 && leftButton == 0 && rightButton == 1){
//         heartbeat_left  = -max_speed;
//         heartbeat_right = -slow_speed;
//     }

//     cmdJsonCmd({'T':cmd_movition_ctrl,'L':heartbeat_left,'R':heartbeat_right});
// }
// function updateMoveButton(key, value) {
//     move_buttons[key] = value;
// }




// var keyMap = {
//     67: "c",
//     82: 'r',
//     69: 'e',
//     70: 'f',
//     72: 'h',
//     73: 'i',
//     75: 'k',
//     77: 'm',
//     74: 'j',
//     76: 'l',
//     79: 'o',
//     85: 'u'
// };

// var ctrl_buttons = {
//     c: 0,
//     r: 0,
//     e: 0,
//     f: 0,
//     h: 0,
//     i: 0,
//     k: 0,
//     m: 0,
//     j: 0,
//     l: 0,
//     o: 0,
//     u: 0
// };

// function updateButton(key, value) {
//     ctrl_buttons[key] = value;
// }

// function cmdProcess() {
//     // Base Light Ctrl
//     if (ctrl_buttons.f == 1){
//         cmdSend(base_ct, 0, 0);
//     }

//     // Photo Capture
//     if (ctrl_buttons.e == 1){
//         cmdSend(pic_cap, 0, 0);
//     }

//     // Function Ctrl
//     if (ctrl_buttons.r == 1){
//         cmdSend(head_ct, 0, 0);
//     }

//     // Gimbal Ctrl
//     if (ctrl_buttons.i == 1){
//         stickSendY -= 10;
//         if (stickSendY < -225) {
//             stickSendY = -225;
//         }
//         joyStickCtrl(stickSendX, stickSendY);
//     } else if (ctrl_buttons.k == 1){
//         stickSendY += 10;
//         if (stickSendY > 115) {
//             stickSendY = 115;
//         }
//         joyStickCtrl(stickSendX, stickSendY);
//     } else if (ctrl_buttons.j == 1){
//         stickSendX -= 10;
//         if (stickSendX < -450) {
//             stickSendX = -450;
//         }
//         joyStickCtrl(stickSendX, stickSendY);
//     } else if (ctrl_buttons.l == 1){
//         stickSendX += 10;
//         if (stickSendX > 450) {
//             stickSendX = 450;
//         }
//         joyStickCtrl(stickSendX, stickSendY);
//     } else if (ctrl_buttons.h == 1){
//         joyStickCtrl(0, 0);
//     }

//     // Gimbal Steady Ctrl
//     if (ctrl_buttons.u == 1){
//         steadyCtrl(0, stickSendY);
//     } else if (ctrl_buttons.o == 1){
//         steadyCtrl(1, stickSendY);
//     } else if (ctrl_buttons.c == 1){
//         lookAhead();
//     }
// }

// document.onkeydown = function (event) {
//     var key = keyMap[event.keyCode];
//     var moveKey = moveKeyMap[event.keyCode];
//     if (key && ctrl_buttons[key] === 0) {
//         updateButton(key, 1);
//         cmdProcess();
//     } else if (moveKey && move_buttons[moveKey] === 0) {
//         updateMoveButton(moveKey, 1);
//         moveProcess();
//     }
// }

// document.onkeyup = function (event) {
//     var key = keyMap[event.keyCode];
//     var moveKey = moveKeyMap[event.keyCode];
//     if (key && ctrl_buttons[key] === 1) {
//         updateButton(key, 0);
//         cmdProcess();
//     } else if (moveKey && move_buttons[moveKey] === 1) {
//         updateMoveButton(moveKey, 0);
//         moveProcess();
//     }
// }

// function lookAhead() {
//     stickLastX = 0;
//     stickLastY = 0;
//     stickSendX = 0;
//     stickSendY = 0;
//     joyStickCtrl(0, 0);
// }