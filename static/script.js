
const registerVideoButton = document.getElementById("takeVideo");
const videoElement = document.createElement("video");
videoElement.controls = true;
document.body.appendChild(videoElement);

registerVideoButton.addEventListener("click", () => {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      const mediaRecorder = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorder.start();

      setTimeout(() => {
        mediaRecorder.stop();
      }, 5000);

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "video/webm" });
        const formData = new FormData();
        formData.append("video", blob, "recorded_video"+ Math.random().toString(36).slice(2) + ".webm");
        console.log();
        fetch("/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => { const res = response.json()
            console.log("Video uploaded successfully:", res);
            return res;
          })
          .catch((error) => {
            console.error("Error uploading video:", error);
          });

        const videoURL = URL.createObjectURL(blob);
        videoElement.src = videoURL;

        stream.getTracks().forEach((track) => track.stop());
      };
    })
    .catch((error) => {
      console.error("Error accessing media devices.", error);
    });
});
