import React from 'react'
import { useRef, useState } from "react";
import Hls from "hls.js";

export default function StreamPlayer() {
  const videoRef = useRef(null);
  const [videoId, setVideoId] = useState("");
  const [status, setStatus] = useState("Ready to load...");
  let hls = null;

  const loadVideo = () => {
    if (!videoId) return alert("Enter Video ID");

    const url = `http://localhost:8080/api/v1/video/${videoId}/index.m3u8`;
    const video = videoRef.current;

    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = url;
      video.play();
      setStatus("Playing natively");
    } else if (Hls.isSupported()) {
      if (hls) hls.destroy();
      hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play();
        setStatus("Playing via HLS.js");
      });
    }
  };

  return (
    <div className="p-10 text-center bg-black text-white min-h-screen">
      <h1 className="text-2xl mb-4">Stream HLS Video</h1>

      <video ref={videoRef} controls muted className="mx-auto w-3/4" />

      <div className="mt-4">
        <input
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
          placeholder="Video ID"
          className="p-2 text-black"
        />
        <button onClick={loadVideo} className="ml-2 bg-blue-600 px-4 py-2">
          Play
        </button>
      </div>

      <p className="mt-4 text-gray-400">{status}</p>
    </div>
  );
}
