---
title: "https nodejs rtmp publisher use openssl"
date: "2019-02-24T12:17:00.001+08:00"
updated: "2019-06-22T20:02:33.749+08:00"
permalink: "/2019/02/https-nodejs-rtmp-publisher-use-openssl.html"
original_url: "https://x8795278.blogspot.com/2019/02/https-nodejs-rtmp-publisher-use-openssl.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3838299486098437726"
tags: ["adobe media server", "Go", "html5", "Node.js", "rtmp", "Tutorial"]
layout: post
---

https nodejs rtmp publisher use openssl
## ---

[![](https://i.imgur.com/M83ZfVD.png)](https://i.imgur.com/M83ZfVD.png)
  

新增https 功能  

由於呢在chrome 呢 如果調用getUserMedia api 則必需要https 代理來小改造一下  

  

**`index.html`**

```html
<!doctype>
<html>
<head>
	<title>MediaRecorder to RTMP Demo</title>
	<script src="/socket.io/socket.io.js"></script>
</head>
<body style="max-width:800px;height:100%;margin:auto;">
<h1>
MediaRecorder to RTMP Demo
</h1>
<label for="option_width" >Size:</label>
<input type="text" id="option_width" value="480"/> &times;
<input type="text" id="option_height" value="360"/>
<br>
<label for="option_url" >RTMP Destination:</label>
<input type="text" id="option_url" value="rtmp://localhost/live"/>
<br>
<button id="button_start">Start streaming</button>
<hr/>
<div>
	<p id="output_message"></p>
	<video id="output_video" autoplay=true></video>
</div>
<hr/>
<textarea readonly="true" id="output_console" cols=91 rows=5>
</textarea>

	<script>
function fail(str){alert(str+"\nPlease download the latest version of Firefox!");location.replace('http://mozilla.org/firefox');}
var output_console=document.getElementById('output_console'),
	output_message=document.getElementById('output_message'),
	output_video=document.getElementById('output_video'),
	option_url=document.getElementById('option_url'),
	option_width=document.getElementById('option_width'),
	option_height=document.getElementById('option_height'),
	button_start=document.getElementById('button_start'),
	height=option_height.value,
	width=option_width.value,
	url=option_url.value='rtmp://'+location.host.split(':')[0]+':1935/live/test';

option_height.onchange=option_height.onkeyup=function(){height=1*this.value;}
option_width.onchange=option_width.onkeyup=function(){width=1*this.value;}
option_url.onchange=option_url.onkeyup=function(){url=this.value;}
button_start.onclick=requestMedia;

function video_show(stream){
	if ("srcObject" in output_video) {
		output_video.srcObject = stream;
	} else {
		output_video.src = window.URL.createObjectURL(stream);
	}
  output_video.addEventListener( "loadedmetadata", function (e) {
	output_message.innerHTML="Local video source size:"+output_video.videoWidth+"x"+output_video.videoHeight;
}, false );
}
function show_output(str){
	output_console.value+="\n"+str;
	output_console.scrollTop = output_console.scrollHeight;
}


navigator.getUserMedia = (navigator.getUserMedia ||
                          navigator.mozGetUserMedia ||
                          navigator.msGetUserMedia ||
                          navigator.webkitGetUserMedia);
if(!navigator.getUserMedia){fail('No getUserMedia() available.');}
if(!MediaRecorder){fail('No MediaRecorder available.');}
var mediaRecorder;
var socket = io.connect("https://localhost", {secure: true});
//({
  // option 1
 // ca: fs.readFileSync("https://localhost:443",'./abels-cert.pem'),
  // option 2. WARNING: it leaves you vulnerable to MITM attacks!
   // requestCert: false,
  //  rejectUnauthorized: false
//});
//var socket = io.
socket.on('message',function(m){
	console.log('recv server message',m);
	show_output('SERVER:'+m);
});
socket.on('fatal',function(m){
	show_output('ERROR: unexpected:'+m);
	alert('Error:'+m);
	mediaRecorder.stop();
	//should reload?
});
socket.on('ffmpeg_stderr',function(m){
	show_output('FFMPEG:'+m);
});
socket.on('disconnect', function () {
	show_output('ERROR: server disconnected!');
	mediaRecorder.stop();
});

function requestMedia(){
	var constraints = { audio: true,
		video:{
	        width: { min: width, ideal: width, max: width },
	        height: { min: height, ideal: height, max: height },
	    }
	};
	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		video_show(stream);//only show locally, not remotely
	
		socket.emit('config_rtmpDestination',url);
		socket.emit('start','start');
		mediaRecorder = new MediaRecorder(stream);
		mediaRecorder.start(2000);
	
		mediaRecorder.onstop = function(e) {
			stream.stop();
				
		}

		mediaRecorder.ondataavailable = function(e) {
			
		  socket.emit("binarystream",e.data);
		  //chunks.push(e.data);
		}
	}).catch(function(err) {
		console.log('The following error occured: ' + err);
		show_output('Local getUserMedia ERROR:'+err);
	});
}
	</script>
</body>
</html>
```

**`server.js`**

```javascript
var express = require('express');
var app = express();
//var http = require('http').Server(app);


//var ffmpeg = require('fluent-ffmpeg');
//var stream = require('stream');
var spawn = require('child_process').spawn;
var fs = require('fs');

app.use(express.static('static'));
const server = require('https').createServer({
 key: fs.readFileSync('abels-key.pem'),
  cert: fs.readFileSync('abels-cert.pem')
 
},app);
//testing

var io = require('socket.io')(server);
spawn('ffmpeg',['-h']).on('error',function(m){
	console.error("FFMpeg not found in system cli; please install ffmpeg properly or make a softlink to ./!");
	process.exit(-1);
});


io.on('connection', function(socket){
	socket.emit('message','Hello from mediarecorder-to-rtmp server!');
	socket.emit('message','Please set rtmp destination before start streaming.');
	
	var ffmpeg_process, feedStream=false;
	socket.on('config_rtmpDestination',function(m){
		if(typeof m != 'string'){
			socket.emit('fatal','rtmp destination setup error.');
			return;
		}
		var regexValidator=/^rtmp:\/\/[^\s]*$/;//TODO: should read config
		if(!regexValidator.test(m)){
			socket.emit('fatal','rtmp address rejected.');
			return;
		}
		socket._rtmpDestination=m;
		socket.emit('message','rtmp destination set to:'+m);
	}); 
	//socket._vcodec='libvpx';//from firefox default encoder
	socket.on('config_vcodec',function(m){
		if(typeof m != 'string'){
			socket.emit('fatal','input codec setup error.');
			return;
		}
		if(!/^[0-9a-z]{2,}$/.test(m)){
			socket.emit('fatal','input codec contains illegal character?.');
			return;
		}//for safety
		socket._vcodec=m;
	}); 	


	socket.on('start',function(m){
		if(ffmpeg_process || feedStream){
			
			socket.emit('fatal','stream already started.');
			return;
		}
		if(!socket._rtmpDestination){
			socket.emit('fatal','no destination given.');
			return;
		}
		
		var ops=[
			'-i','-',
			'-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'zerolatency',
			'-an', //TODO: give up audio for now...
			//'-async', '1', 
			'-filter_complex', 'aresample=44100', //necessary for trunked streaming?
			//'-strict', 'experimental', '-c:a', 'aac', '-b:a', '128k',
			'-bufsize', '1000',
			'-f', 'flv', socket._rtmpDestination
		];
		
		console.log(socket._rtmpDestination);
		ffmpeg_process=spawn('ffmpeg', ops);
		feedStream=function(data){
			
			ffmpeg_process.stdin.write(data);
			//write exception cannot be caught here.	
		}

		ffmpeg_process.stderr.on('data',function(d){
			socket.emit('ffmpeg_stderr',''+d);
		});
		ffmpeg_process.on('error',function(e){
			console.log('child process error'+e);
			socket.emit('fatal','ffmpeg error!'+e);
			feedStream=false;
			socket.disconnect();
		});
		ffmpeg_process.on('exit',function(e){
			console.log('child process exit'+e);
			socket.emit('fatal','ffmpeg exit!'+e);
			socket.disconnect();
		});
	});

	socket.on('binarystream',function(m){
		if(!feedStream){
			socket.emit('fatal','rtmp not set yet.');
			return;
		}
		feedStream(m);
	});
	socket.on('disconnect', function () {
		feedStream=false;
		if(ffmpeg_process)
		try{
			ffmpeg_process.stdin.end();
			ffmpeg_process.kill('SIGINT');
		}catch(e){console.warn('killing ffmoeg process attempt failed...');}
	});
	socket.on('error',function(e){
		
		console.log('socket.io error:'+e);
	});
});

io.on('error',function(e){
	console.log('socket.io error:'+e);
});

//http.listen(8888, function(){
 // console.log('http and websocket listening on *:8888');
//});

server.listen(443, function(){
  console.log('https and websocket listening on *:443');
});

process.on('uncaughtException', function(err) {
    // handle the error safely
    console.log(err)
    // Note: after client disconnect, the subprocess will cause an Error EPIPE, which can only be caught this way.
})
```
