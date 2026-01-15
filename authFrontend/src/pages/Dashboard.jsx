import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    // 🔒 NOT logged in → go to login
    if (!token) {
      navigate("/");
      return;
    }

    // ✅ Logged in → load user
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else {
      // Fallback until backend sends user object
      setUser({
        name: "User",
        email: "Logged-in user",
      });
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/"); // ✅ back to login
  };


  if (!user) return null;

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* ================= HEADER ================= */}
      <header className="flex items-center justify-between px-8 py-4 bg-white shadow">
        <h1 className="text-xl font-bold text-gray-800">
          LocalStorage Dashboard
        </h1>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold"
          >
            {user.name.charAt(0).toUpperCase()}
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded shadow-lg border">
              <div className="px-4 py-3 border-b">
                <p className="font-medium text-gray-800">{user.name}</p>
                <p className="text-sm text-gray-500">{user.email}</p>
              </div>

              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* ================= MAIN ================= */}
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        <h2 className="text-3xl font-bold mb-8">
          Welcome, {user.name} 👋
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl">
          <div
            onClick={() => navigate("/stream")}
            className="cursor-pointer bg-white rounded-xl shadow hover:shadow-lg transition p-6 text-center"
          >
            <h3 className="text-xl font-semibold mb-2">Stream Video</h3>
            <p className="text-gray-600">
              Watch videos using secure streaming
            </p>
            <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">
              Go →
            </button>
          </div>

          <div
            onClick={() => navigate("/storage")}
            className="cursor-pointer bg-white rounded-xl shadow hover:shadow-lg transition p-6 text-center"
          >
            <h3 className="text-xl font-semibold mb-2">
              Upload & Stream
            </h3>
            <p className="text-gray-600">
              Upload videos and stream instantly
            </p>
            <button className="mt-4 px-4 py-2 bg-green-600 text-white rounded">
              Upload →
            </button>
          </div>
        </div>
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="bg-white text-center py-4 text-gray-500 text-sm border-t">
        © 2026 LocalStorage · Secure Media Platform
      </footer>
    </div>
  );
}
