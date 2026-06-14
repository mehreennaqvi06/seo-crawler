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

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
    alert("Please enter a valid URL");
    return;
  }

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
  <div className="app">

    <div className="hero">

      <div className="logo">
        SEO Crawler
      </div>

      <div className="badge">
        ✨ AI Powered SEO Analysis
      </div>

      <h1 className="hero-title">
        Scan your website
      </h1>

      <p className="hero-subtitle">
        Analyze pages, metadata, headings and crawl performance
        in real time.
      </p>

    </div>

    <div className="scan-card">

      <label className="input-label">
        Website URL
      </label>

      <input
        className="url-input"
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://example.com"
      />

      <div className="limit-section">

  <p>Page Limit: {limit}</p>

  <input
    type="range"
    min="1"
    max="100"
    value={limit}
    onChange={(e) => setLimit(Number(e.target.value))}
  />

</div>

      <div className="button-group">

  <button
    className="crawl-btn"
    onClick={startCrawl}
  >
    Analyze Website →
  </button>

  <button
    className="status-btn"
    onClick={checkStatus}
    disabled={!jobId}
  >
    Check Status
  </button>

</div>
    
    <div className="progress-section-card">

  <div className="progress-container">
    <div
      className="progress-bar"
      style={{ width: `${progress}%` }}
    />
  </div>

  <p className="progress-label">
    {progress}% Complete
  </p>

</div>

    </div>

    {jobId && (
      <div className="stats-grid">

        <div className="stat-card">
          <h4>Job ID</h4>
          <span>{jobId}</span>
        </div>

        <div className="stat-card">
          <h4>Status</h4>
          <span className={`status-${status}`}>
            {status || "Waiting"}
          </span>
        </div>

        <div className="stat-card">
          <h4>Pages</h4>
          <span>{pages.length}</span>
        </div>

      </div>
    )}

    {jobId && (
      <div className="progress-section">

        <div className="progress-header">
          Crawl Progress
        </div>

        <div className="progress-container">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>

        <p>{progress}% Complete</p>

      </div>
    )}

    {pages.length > 0 && (
      <div className="results-card">

        <div className="results-header">

          <h2>Crawl Results</h2>

          <button
            className="sort-btn"
            onClick={sortByStatus}
          >
            Sort Status
          </button>

        </div>

        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Title</th>
              <th>H1</th>
              <th>Status</th>
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

      </div>
    )}

  </div>
);
}

export default App;

