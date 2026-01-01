import React from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 gap-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <button
        onClick={() => navigate("/stream")}
        className="px-6 py-3 bg-blue-600 text-white rounded"
      >
        Stream Video
      </button>

      <button
        onClick={() => navigate("/storage")}
        className="px-6 py-3 bg-green-600 text-white rounded"
      >
        Upload & Stream Video
      </button>
    </div>
  );
}
