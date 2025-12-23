import React from 'react'
import { useState } from "react";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    dateOfBirth: "",
    password: "",
    password_confirm: "",
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5000/api/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    alert(data.message || data.error);
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-gray-100 to-gray-200">
      <div className="w-full max-w-md bg-white shadow-lg rounded-2xl p-8">
        <h1 className="text-3xl font-semibold text-center text-gray-800 mb-6">
          Register
        </h1>

        <form onSubmit={handleRegister} className="space-y-5">
          <input
            name="username"
            placeholder="Username"
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded-md bg-white focus:ring-2 focus:ring-green-500 outline-none"
          />

          <input
            name="email"
            placeholder="Email"
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded-md bg-white focus:ring-2 focus:ring-green-500 outline-none"
          />

          <input
            type="date"
            name="dateOfBirth"
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded-md bg-white focus:ring-2 focus:ring-green-500 outline-none"
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded-md bg-white focus:ring-2 focus:ring-green-500 outline-none"
          />

          <input
            type="password"
            name="password_confirm"
            placeholder="Confirm Password"
            onChange={handleChange}
            className="w-full px-4 py-2 border rounded-md bg-white focus:ring-2 focus:ring-green-500 outline-none"
          />

          <button
            type="submit"
            className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition"
          >
            Register
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <a href="/" className="text-blue-600 hover:underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}
