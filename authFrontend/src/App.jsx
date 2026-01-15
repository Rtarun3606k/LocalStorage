import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard"; 
import StreamPlayer from "./pages/StreamPlayer";       
import StorageDashboard from "./pages/StorageDashboard"; 

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/stream" element={<StreamPlayer />} />
        <Route path="/storage" element={<StorageDashboard />} />
        
      </Routes>
    </BrowserRouter>
  );
}
