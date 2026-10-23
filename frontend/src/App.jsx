import { useEffect, useState } from "react";
import "./App.css";
import { searchBugs, checkBackendHealth } from "./services/api";


function App() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("All Languages");

  const [backendOnline, setBackendOnline] = useState(false);
  const [backendChecking, setBackendChecking] = useState(true);

  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedBug, setSelectedBug] = useState(null);
  useEffect(() => {
    let active = true;

    const checkHealth = async () => {
      try {
        await checkBackendHealth();

        if (active) {
          setBackendOnline(true);
        }
      } catch {
        if (active) {
          setBackendOnline(false);
        }
      } finally {
        if (active) {
          setBackendChecking(false);
        }
      }
    };

    checkHealth();

    const interval = setInterval(checkHealth, 10000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);


  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError("Please describe your programming error.");
      setResults([]);
      setSearched(false);
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);
    setSearched(false);
    setSelectedBug(null);

    try {
      const data = await searchBugs(query.trim(), language);

      setResults(data.results);
      setSearched(true);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to ShadowTrace. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const chooseExample = (example) => {
    setQuery(example);
    setError("");
  };

  return (
    <div className="app">
      <nav className="navbar">
  <a className="brand" href="#home">
    <div className="brand-icon">S</div>
    <span>ShadowTrace</span>
  </a>

  <div className="nav-links">
    <a className="nav-link active" href="#home">
      Home
    </a>

    <a className="nav-link" href="#results">
      Explore Bugs
    </a>

    <a className="nav-link" href="#features">
      How It Works
    </a>

    <a className="nav-link" href="#about">
      About
    </a>
  </div>

<div className="nav-right">
  <span
    className={`status-dot ${
      backendChecking
        ? "status-checking"
        : backendOnline
          ? "status-online"
          : "status-offline"
    }`}
  ></span>

  <span className="nav-label">
    {backendChecking
      ? "Checking Backend"
      : backendOnline
        ? "Backend Online"
        : "Backend Offline"}
  </span>
</div>

</nav>

      <main className="main-content" id="home">
        <section className="hero">
          <div className="badge">
            <span>✦</span> INTELLIGENT DEBUGGING
          </div>

          <h1>
            Every bug has a
            <br />
            <span>story behind it.</span>
          </h1>

          <p className="hero-description">
            Describe your error. Discover similar bugs, understand their
            root causes, and find solutions from our searchable bug database.
          </p>

          <form className="search-panel" onSubmit={handleSearch}>
            <label htmlFor="bug-query">DESCRIBE YOUR ERROR</label>

            <textarea
              id="bug-query"
              placeholder="e.g. My Java program crashes when I access an uninitialized object..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={4}
            />

            <div className="search-controls">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                aria-label="Programming language"
              >
                <option>All Languages</option>
                <option>Java</option>
                <option>Python</option>
                <option>C</option>
                <option>C++</option>
                <option>JavaScript</option>
              </select>

              <button type="submit" disabled={loading}>
                {loading ? "Searching..." : "Find Solutions"}
                {!loading && <span> →</span>}
              </button>
            </div>
          </form>

          <div className="quick-search">
            <span>TRY SEARCHING</span>

            {[
              "NullPointerException",
              "IndexError",
              "Segmentation fault",
            ].map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => chooseExample(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </section>

        {error && (
          <section className="search-feedback error-message" role="alert">
            {error}
          </section>
        )}

        {loading && (
          <section className="search-feedback">
            Searching the bug database...
          </section>
        )}

        {searched && (
          <section className="results-section" id="results">
            <div className="results-heading">
              <div>
                <span className="results-eyebrow">SEARCH RESULTS</span>
                <h2>Related bugs</h2>
              </div>

              <span className="result-count">
                {results.length} {results.length === 1 ? "match" : "matches"}
              </span>
            </div>

            {results.length === 0 ? (
              <div className="empty-results">
                <h3>No matching bugs found</h3>
                <p>
                  Try describing the error differently or choose another
                  programming language.
                </p>
              </div>
            ) : (
              <div className="results-grid">
                {results.map((bug) => (
                  <article className="result-card" key={bug.id}>
                    <div className="result-card-top">
                      <span className="language-tag">{bug.language}</span>

                      <span className="similarity">
                        {(bug.score * 100).toFixed(1)}% similarity
                      </span>
                    </div>

                    <h3>{bug.title}</h3>

                    <p className="bug-description">{bug.description}</p>

                    <div className="root-cause">
                      <span>ROOT CAUSE</span>
                      <p>{bug.root_cause}</p>
                    </div>

                    <button
                      className="solution-button"
                      onClick={() => setSelectedBug(bug)}
                    >
                      View solution <span>→</span>
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {selectedBug && (
          <div
            className="modal-backdrop"
            onMouseDown={(e) => {
              if (e.target === e.currentTarget) {
                setSelectedBug(null);
              }
            }}
          >
            <section
              className="solution-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="solution-title"
            >
              <button
                className="modal-close"
                onClick={() => setSelectedBug(null)}
                aria-label="Close solution"
              >
                ×
              </button>

              <span className="results-eyebrow">BUG EXPLANATION</span>

              <h2 id="solution-title">{selectedBug.title}</h2>

              <span className="language-tag">{selectedBug.language}</span>

              <h3>Root cause</h3>
              <p>{selectedBug.root_cause}</p>

              <h3>Suggested solution</h3>
              <p>{selectedBug.solution}</p>


<div className="code-comparison">
  <h3>❌ Buggy code</h3>
  <pre className="code-block">
    <code>
      {selectedBug.buggy_code || "Buggy code not available."}
    </code>
  </pre>

  <h3>✅ Corrected code</h3>
  <pre className="code-block">
    <code>
      {selectedBug.fixed_code || "Corrected code not available."}
    </code>
  </pre>
</div>


              <p className="solution-note">
                This is a suggested fix based on a similar recorded issue.
                Verify that it applies to your specific problem.
              </p>
            </section>
          </div>
        )}

        <section className="features" id="features">
          <div className="section-heading">
            <span>WHY SHADOWTRACE?</span>
            <h2>Debug smarter, not harder.</h2>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <div className="feature-icon purple">⌕</div>
              <h3>Semantic Search</h3>
              <p>
                Find relevant bugs by meaning, even when the descriptions
                use different words.
              </p>
              <span className="feature-number">01 / SEARCH</span>
            </article>

            <article className="feature-card">
              <div className="feature-icon blue">&lt;/&gt;</div>
              <h3>Understand the Cause</h3>
              <p>
                Explore why an error occurs and learn how similar problems
                were solved.
              </p>
              <span className="feature-number">02 / ANALYSE</span>
            </article>

            <article className="feature-card">
              <div className="feature-icon green">↗</div>
              <h3>Discover Solutions</h3>
              <p>
                Retrieve useful fixes from a searchable collection of
                programming errors.
              </p>
              <span className="feature-number">03 / RESOLVE</span>
            </article>
          </div>
        </section>

        <footer id="about">
          <div className="footer-brand">ShadowTrace</div>
          <span>Built for developers, powered by intelligent search.</span>
          <span className="footer-status">VERSION 1.0</span>
        </footer>
      </main>
    </div>
  );
}

export default App;