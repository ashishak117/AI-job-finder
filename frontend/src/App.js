import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

const App = () => {
  const [resume, setResume] = useState(null);
  const [jobResults, setJobResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => setResume(e.target.files[0]);

  const handleUpload = async () => {
    if (!resume) {
      setError("Please upload a resume!");
      return;
    }

    setLoading(true);
    setError("");
    setJobResults([]);
    const formData = new FormData();
    formData.append("resume", resume);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setJobResults(response.data.job_recommendations);
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="container mt-5">
      <div className="card p-4 shadow">
        <h1>AI Job Finder</h1>
        <input type="file" className="form-control mb-3" onChange={handleFileChange} />
        <button
          onClick={handleUpload}
          className="btn btn-primary w-100"
          disabled={loading}
        >
          {loading ? "Processing..." : "Upload & Get Jobs"}
        </button>
        {error && <div className="alert alert-danger mt-3">{error}</div>}
      </div>

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
                  <td>
                    <a href={job.url} target="_blank" rel="noopener noreferrer">
                      {job.title}
                    </a>
                  </td>
                  <td>{job.company}</td>
                  <td>{job.score}%</td>
                  <td>
                    <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-primary">
                      Apply
                    </a>
                  </td>
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