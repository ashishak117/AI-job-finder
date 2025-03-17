import React, { useState } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [resume, setResume] = useState(null);
  const [jobResults, setJobResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegister = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/register", { email, password });
      toast.success("Registration successful! You can now log in.");
    } catch (error) {
      toast.error(error.response?.data?.error || "Registration failed!");
    }
  };

  const handleLogin = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/login", { email, password });
      setIsLoggedIn(true);
      toast.success("Login successful!");
    } catch (error) {
      toast.error(error.response?.data?.error || "Invalid credentials!");
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setEmail("");
    setPassword("");
    toast.info("Logged out successfully!");
  };

  const handleUpload = async () => {
    if (!resume || !isLoggedIn) {
      setError("Please login and upload a resume!");
      return;
    }

    setLoading(true);
    setError("");
    setJobResults([]);
    const formData = new FormData();
    formData.append("resume", resume);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload-resume", formData, {
        auth: { username: email, password: password }, // Basic Auth
      });
      setJobResults(response.data.job_recommendations);
      toast.success("Job recommendations loaded!");
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    }
    setLoading(false);
  };

  return (
    <div className="container mt-5">
      <ToastContainer />
      {isLoggedIn ? (
        <div className="mb-3 text-center">
          <h2>Welcome, {email.split("@")[0]}!</h2>
          <button onClick={handleLogout} className="btn btn-danger">Logout</button>
        </div>
      ) : (
        <div className="card p-4 shadow">
          <h2>User Authentication</h2>
          <input type="email" className="form-control mb-3" placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
          <input type="password" className="form-control mb-3" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
          <button onClick={handleLogin} className="btn btn-primary w-100 mb-2">Login</button>
          <button onClick={handleRegister} className="btn btn-secondary w-100">Register</button>
        </div>
      )}

      {isLoggedIn && (
        <div className="card p-4 shadow mt-4">
          <h2>Upload Resume</h2>
          <input type="file" className="form-control mb-3" onChange={(e) => setResume(e.target.files[0])} />
          <button onClick={handleUpload} className="btn btn-warning w-100" disabled={loading}>
            {loading ? "Processing..." : "Upload Resume & Get Jobs"}
          </button>
          {error && <div className="alert alert-danger mt-3">{error}</div>}
        </div>
      )}

      {jobResults.length > 0 && (
        <div className="mt-4">
          <h3>Job Recommendations</h3>
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Title</th>
                <th>Company</th>
                <th>Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {jobResults.map((job, index) => (
                <tr key={index}>
                  <td><a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a></td>
                  <td>{job.company}</td>
                  <td>{job.score}%</td>
                  <td><a href={job.url} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-primary">Apply</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default App;