//------------------------------------------------
//          Media Recorder & Control
//------------------------------------------------
navigator.mediaDevices.getUserMedia({audio:true})
	.then(stream => {
		rec = new MediaRecorder(stream);
		rec.ondataavailable = e => {
			audioChunks.push(e.data);
			if (rec.state == "inactive"){
        let blob = new Blob(audioChunks,{type:'audio/x-mpeg-3'});
        recordedAudio.src = URL.createObjectURL(blob);
        recordedAudio.controls=true;
        recordedAudio.autoplay=false;
        audioDownload.href = recordedAudio.src;
        audioDownload.download = 'mp3';
        audioDownload.innerHTML = 'download';
     }
		}
	})
	.catch(e=>console.log(e));

//------------------------------------------------
//          Start Recoding
//------------------------------------------------
startRecord.onclick = e => {
  startRecord.disabled = true;
  stopRecord.disabled=false;
  audioChunks = [];
  rec.start();
}

//------------------------------------------------
//          Stop Recoding
//------------------------------------------------
stopRecord.onclick = e => {
  startRecord.disabled = false;
  stopRecord.disabled=true;
  rec.stop();
}
