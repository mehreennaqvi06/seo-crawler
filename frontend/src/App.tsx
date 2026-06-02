import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [limit, setLimit] = useState(10);
  const [jobId, setJobId] = useState<number | null>(null);
  const [status, setStatus] = useState("");
  const [pages, setPages] = useState<any[]>([]);

  const startCrawl = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/jobs",
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
      `http://127.0.0.1:8000/jobs/${jobId}`
    );

    console.log(response.data);

    setStatus(response.data.status);

    if (response.data.status === "completed") {
      loadPages();
    }
  };

  const loadPages = async () => {
    if (!jobId) return;

    const response = await axios.get(
      `http://127.0.0.1:8000/jobs/${jobId}/pages`
    );

    setPages(response.data);
  };

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(() => {
      checkStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div style={{ padding: "40px" }}>
      <h1>SEO Crawler</h1>

      <div>
        <label>URL:</label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          style={{ marginLeft: "10px", width: "400px" }}
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

      {pages.length > 0 && (
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
      )}

    </div>
  );
}

export default App;