import React from 'react'
import { useRef, useState } from "react";
import Hls from "hls.js";

export default function StorageDashboard() {
  const videoRef = useRef(null);
  const [videoId, setVideoId] = useState("");
  const [progress, setProgress] = useState(0);

  const uploadFile = () => {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return alert("Select file");

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.upload.onprogress = (e) => {
      setProgress(Math.round((e.loaded / e.total) * 100));
    };

    xhr.onload = () => {
      const id = xhr.responseText.split(": ")[1];
      setVideoId(id);
    };

    xhr.open("POST", "http://localhost:8080/api/v1/video/upload");
    xhr.send(formData);
  };

  const playVideo = () => {
    const url = `http://localhost:8080/api/v1/video/${videoId}/index.m3u8`;
    const hls = new Hls();
    hls.loadSource(url);
    hls.attachMedia(videoRef.current);
    hls.on(Hls.Events.MANIFEST_PARSED, () => videoRef.current.play());
  };

  return (
    <div className="p-10 bg-gray-900 text-white min-h-screen">
      <h1 className="text-2xl mb-6">Storage Engine</h1>

      <input id="fileInput" type="file" />
      <button onClick={uploadFile} className="block mt-2 bg-blue-600 px-4 py-2">
        Upload
      </button>

      {progress > 0 && <p>Progress: {progress}%</p>}

      <video ref={videoRef} controls className="mt-6 w-full" />

      <input
        value={videoId}
        onChange={(e) => setVideoId(e.target.value)}
        placeholder="Video ID"
        className="text-black p-2 mt-2"
      />
      <button onClick={playVideo} className="ml-2 bg-green-600 px-4 py-2">
        Play
      </button>
    </div>
  );
}
