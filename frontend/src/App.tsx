import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [limit, setLimit] = useState(10);
  const [jobId, setJobId] = useState<number | null>(null);
  const [status, setStatus] = useState("");
  const [pages, setPages] = useState<any[]>([]);
  const [progress, setProgress] = useState(0);

  const startCrawl = async () => {
    try {
      const response = await axios.post(
        "https://seo-crawler-production-b521.up.railway.app/jobs",
        null,
        {
          params: {
            url,
            limit,
          },
        }
      );

      console.log(response.data);
      setJobId(response.data.job_id);
      
      alert("Job created!");
    } catch (error) {
      console.error(error);
      alert("Failed to create job");
    }
  };

  const checkStatus = async () => {
    if (!jobId) return;

    const response = await axios.get(
      `https://seo-crawler-production-b521.up.railway.app/jobs/${jobId}`
    );

    console.log(response.data);

    setStatus(response.data.status);

    if (response.data.status === "queued") {
      setProgress(25);
    }

    if (response.data.status === "running") {
      setProgress(75);
    }

    if (response.data.status === "completed") {
      setProgress(100);
      loadPages();
    }
  };

  const loadPages = async () => {
    if (!jobId) return;

    const response = await axios.get(
      `https://seo-crawler-production-b521.up.railway.app/jobs/${jobId}/pages`
    );

    setPages(response.data);
  };

  const sortByStatus = () => {
    const sorted = [...pages].sort(
      (a, b) => a.status_code - b.status_code
    );

    setPages(sorted);
  };

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(() => {
      checkStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div className="container">
      <h1 className="title">SEO Crawler</h1>

      <div>
        <label>URL:</label>
        <input
          className="url-input"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
        />
      </div>

      <br />

      <div>
        <label>Page Limit: {limit}</label>
        <br />
        <input
          type="range"
          min="1"
          max="100"
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
        />
      </div>

      <br />

      <button onClick={startCrawl}>Start Crawl</button>

      <button onClick={checkStatus}>
        Check Status
      </button>

      {jobId && (
        <p>Job ID: {jobId}</p>
      )}

      {status && (
        <p>Status: {status}</p>
      )}

      <div style={{ width: "400px", margin: "20px auto" }}>
        <progress value={progress} max="100" style={{ width: "100%" }} />
        <p>{progress}%</p>
      </div>
      
      

      {pages.length > 0 && (
        <>
          <button onClick={sortByStatus}>
            Sort by Status Code
          </button>

          <table border={1}>
          <thead>
            <tr>
              <th>URL</th>
              <th>Title</th>
              <th>H1</th>
              <th>Status Code</th>
            </tr>
          </thead>

          <tbody>
            {pages.map((page, index) => (
              <tr key={index}>
                <td>{page.url}</td>
                <td>{page.title}</td>
                <td>{page.h1}</td>
                <td>{page.status_code}</td>
              </tr>
            ))}
          </tbody>
          </table>
  </>
)}

    </div>
  );
}

export default App;

