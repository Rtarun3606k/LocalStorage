import React from "react";
import { useRef, useState } from "react";
import Hls from "hls.js";

export default function StorageDashboard() {
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  const [mediaId, setMediaId] = useState("");
  const [mediaType, setMediaType] = useState("");
  const [progress, setProgress] = useState(0);

  const uploadFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type.startsWith("image/")) setMediaType("image");
    else if (file.type.startsWith("video/")) setMediaType("video");
    else return alert("Unsupported file type");

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        setProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status !== 200) return alert("Upload failed");
      const id = xhr.responseText.split(": ")[1];
      setMediaId(id);
    };

    xhr.open("POST", "http://localhost:8080/api/v1/video/upload");
    xhr.send(formData);
  };

  const playVideo = () => {
    if (mediaType !== "video") return;

    const url = `http://localhost:8080/api/v1/video/${mediaId}/index.m3u8`;
    const video = videoRef.current;

    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = url;
      video.play();
    } else if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => video.play());
    }
  };

  return (
    <div className="p-10 bg-gray-900 text-white min-h-screen">
      <h1 className="text-2xl mb-6">Storage Engine</h1>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={uploadFile}
      />

      {/* Trigger button */}
      <button
        onClick={() => fileInputRef.current.click()}
        className="bg-blue-600 px-4 py-2 rounded"
      >
        Upload File
      </button>

      {progress > 0 && <p className="mt-2">Progress: {progress}%</p>}

      {mediaType === "image" && (
        <img
          src={`http://localhost:8080/api/v1/image/${mediaId}`}
          className="mt-6 max-w-full rounded"
        />
      )}

      {mediaType === "video" && (
        <>
          <video ref={videoRef} controls className="mt-6 w-full rounded" />
          <button
            onClick={playVideo}
            className="mt-2 bg-green-600 px-4 py-2 rounded"
          >
            Play Video
          </button>
        </>
      )}
    </div>
  );
}
