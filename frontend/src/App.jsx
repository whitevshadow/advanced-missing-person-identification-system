import { useMemo, useState, useEffect } from "react";
import AuthPanel from "./components/AuthPanel";
import { loginUser, registerUser, fetchCurrentUser, setAuthToken } from "./api";

const navItems = [
  { id: "dashboard", label: "Dashboard" },
  { id: "register", label: "Register Case" },
  { id: "cases", label: "All Cases" },
  { id: "found", label: "Found Persons" },
  { id: "admin", label: "Admin Panel" },
];

const dashboardMatches = [
  {
    rank: 1,
    name: "Arjun Sharma → Sighting #4821",
    confidence: 91,
    details: "Jawline · Eye spacing · Nose bridge match",
    stroke: "var(--gold)",
  },
  {
    rank: 2,
    name: "Priya Devi → Sighting #4799",
    confidence: 78,
    details: "Cheekbone · Forehead structure partial",
    stroke: "#a0a0a0",
  },
  {
    rank: 3,
    name: "Ravi Kumar → Sighting #4755",
    confidence: 64,
    details: "Age regression · Low quality input",
    stroke: "#8b5a2b",
  },
];

const recentCases = [
  {
    name: "Meera Krishnan",
    meta: ["Age 8 · Female", "Last seen: Chennai", "Reported 2 days ago"],
    status: "Missing",
    statusClass: "s-missing",
  },
  {
    name: "Arjun Sharma",
    meta: ["Age 34 · Male", "Last seen: Mumbai"],
    status: "Match 91%",
    statusClass: "s-match",
    confidence: 91,
    fill: "var(--gold)",
  },
  {
    name: "Lakshmi Patel",
    meta: ["Age 62 · Female", "Reunited with family"],
    status: "Found",
    statusClass: "s-found",
  },
];

const allCases = [
  {
    name: "Rahul Nair",
    meta: ["Age 22 · Male", "Hyderabad · 4d ago"],
    status: "Missing",
    statusClass: "s-missing",
  },
  {
    name: "Priya Devi",
    meta: ["Age 29 · Female", "Pune · 1d ago"],
    status: "Match 78%",
    statusClass: "s-match",
    confidence: 78,
    fill: "#a0a0a0",
  },
  {
    name: "Suresh Babu",
    meta: ["Age 55 · Male", "Bengaluru · 7d ago"],
    status: "Missing",
    statusClass: "s-missing",
  },
  {
    name: "Ananya Singh",
    meta: ["Age 17 · Female", "Delhi · Reunited"],
    status: "Found",
    statusClass: "s-found",
  },
  {
    name: "Ravi Kumar",
    meta: ["Age 41 · Male", "Chennai · 3d ago"],
    status: "Match 64%",
    statusClass: "s-match",
    confidence: 64,
    fill: "#c48040",
  },
  {
    name: "Kavya Reddy",
    meta: ["Age 13 · Female", "Visakhapatnam · 2d ago"],
    status: "Missing",
    statusClass: "s-missing",
  },
];

const foundPeople = [
  {
    name: "Lakshmi Patel",
    sub: "Age 62 · Chennai\nAI match confidence: 94%\nFound: Coimbatore shelter",
  },
  {
    name: "Ananya Singh",
    sub: "Age 17 · Delhi\nAI match confidence: 88%\nFound: Railway station",
  },
  {
    name: "Dinesh Varma",
    sub: "Age 45 · Mumbai\nAI match confidence: 96%\nFound: Hospital ward",
  },
  {
    name: "Sneha Mehta",
    sub: "Age 8 · Ahmedabad\nAI match confidence: 91%\nFound: Community center",
  },
];

const adminMatches = [
  {
    rank: 1,
    name: "Arjun Sharma",
    confidence: 91,
    details: "High confidence — review photo pair",
    stroke: "var(--gold)",
  },
  {
    rank: 2,
    name: "Priya Devi",
    confidence: 78,
    details: "Moderate — verify in person",
    stroke: "#a0a0a0",
  },
  {
    rank: 3,
    name: "Ravi Kumar",
    confidence: 64,
    details: "Low quality image — flag for re-upload",
    stroke: "#8b5a2b",
  },
];

const faqs = {
  "how do i report":
    "Go to Register Case in the sidebar. Upload a clear photo and fill in the details. Our AI will process the image and start matching automatically.",
  "how does ai work":
    "We use OpenCV YuNet for face detection and SFace ONNX for generating 128-dimensional face embeddings. Matches are ranked by cosine similarity — you see the top 3 results with confidence percentages.",
  "blurry photo":
    "Upload it anyway! Our AI applies CLAHE enhancement and super-resolution preprocessing before extracting face features. Even low-quality images can be processed.",
  contact:
    "You can reach the system admin or check the Alerts section. Email notifications are sent automatically when a match is found above 60% confidence.",
  "what is recovery rate":
    "The percentage of registered missing persons who have been found and reunited with their families. Currently at 45.4%.",
};

function AvatarFace() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="var(--muted)">
      <circle cx="14" cy="10" r="6" />
      <path d="M4 26c0-5.5 4.5-10 10-10s10 4.5 10 10" fill="var(--muted)" />
    </svg>
  );
}

function Ring({ value, stroke }) {
  return (
    <div className="ring-wrap">
      <svg width="36" height="36" viewBox="0 0 36 36">
        <circle cx="18" cy="18" r="14" fill="none" stroke="var(--border)" strokeWidth="3" />
        <circle
          cx="18"
          cy="18"
          r="14"
          fill="none"
          stroke={stroke}
          strokeWidth="3"
          strokeDasharray={`${Math.round((value / 100) * 88)} 88`}
          strokeLinecap="round"
        />
      </svg>
      <span className="ring-val" style={{ color: stroke }}>
        {value}%
      </span>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([
    {
      type: "bot",
      text: "Hello! I can help with reporting missing persons, understanding how AI matching works, or navigating this system. What do you need?",
    },
  ]);
  const [geoEnabled, setGeoEnabled] = useState(true);
  const [uploadLabel, setUploadLabel] = useState("Drop photo here or click to upload");

  // Authentication state and handlers
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const user = await fetchCurrentUser();
        if (mounted) setCurrentUser(user);
      } catch (err) {
        setAuthToken(null);
        if (mounted) setCurrentUser(null);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const handleLogin = async ({ email, password }) => {
    const resp = await loginUser({ email, password });
    if (resp?.access_token) {
      setAuthToken(resp.access_token);
      const user = await fetchCurrentUser();
      setCurrentUser(user);
    }
  };

  const handleRegister = async (payload) => {
    await registerUser(payload);
    await handleLogin({ email: payload.email, password: payload.password });
  };

  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
  };

  const activePage = useMemo(() => page, [page]);

  const openChatReply = () => setChatOpen((current) => !current);

  const sendChat = () => {
    const query = chatInput.trim();
    if (!query) return;

    const matchedKey = Object.keys(faqs).find((key) => query.toLowerCase().includes(key));
    const reply = matchedKey
      ? faqs[matchedKey]
      : "I'll connect you with a human operator for this query. In the meantime, you can explore the All Cases section or register a new case.";

    setChatMessages((prev) => [
      ...prev,
      { type: "user", text: query },
      { type: "bot", text: reply },
    ]);
    setChatInput("");
  };

  const handleSubmitCase = () => {
    window.alert("Case submitted! AI processing initiated.");
  };

  const renderPage = () => {
    if (activePage === "register") {
      return (
        <div id="page-register" className="page-shell">
          <div className="topbar">
            <div className="page-title">Register New Case</div>
            <button className="btn btn-ghost" type="button" onClick={() => setPage("cases")}>
              ← Back to Cases
            </button>
          </div>
          <div className="content">
            <div className="alert-quality" style={{ maxWidth: 580, marginBottom: 14 }}>
              <strong>AI photo tip:</strong> Upload the clearest photo available. Our AI will auto-enhance blurry or low-light images using CLAHE + super-resolution before extracting face embeddings.
            </div>
            <div className="form-grid">
              <div
                className="field upload-zone"
                onDragOver={(event) => event.preventDefault()}
                onClick={() => setUploadLabel("✓ Photo selected — AI will auto-enhance if needed")}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ margin: "0 auto 8px" }}>
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <span id="upload-label">{uploadLabel}</span>
                <span style={{ fontSize: 10, marginTop: 4 }}>JPG, PNG, HEIC — AI will enhance if blurry</span>
              </div>
              <div className="field">
                <label>Full Name</label>
                <input type="text" placeholder="Enter full name" />
              </div>
              <div className="field">
                <label>Age</label>
                <input type="number" placeholder="Age" />
              </div>
              <div className="field">
                <label>Gender</label>
                <select defaultValue="Select">
                  <option>Select</option>
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
                </select>
              </div>
              <div className="field">
                <label>Last Known Location</label>
                <input type="text" placeholder="City, State" />
              </div>
              <div className="field">
                <label>Date Missing</label>
                <input type="date" />
              </div>
              <div className="field">
                <label>Reporter Contact</label>
                <input type="text" placeholder="Phone or email" />
              </div>
              <div className="field field-full">
                <label>Additional Details</label>
                <textarea placeholder="Clothing, distinguishing marks, circumstances..." />
              </div>
              <div className="geo-row">
                <div className={geoEnabled ? "toggle on" : "toggle"} onClick={() => setGeoEnabled((value) => !value)} />
                <span>Enable geolocation tracking (optional)</span>
              </div>
              <div className="map-placeholder" id="map-area">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="1.5">
                  <path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                Geolocation map preview — tap to pin last known location
              </div>
              <div className="form-actions">
                <button className="btn btn-primary" type="button" onClick={handleSubmitCase}>
                  Submit & Run AI Match
                </button>
                <button className="btn btn-ghost" type="button">
                  Save Draft
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (activePage === "cases") {
      return (
        <div id="page-cases" className="page-shell">
          <div className="topbar">
            <div className="page-title">All Cases</div>
            <div className="topbar-right">
              <div className="search-box">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="6.5" cy="6.5" r="4" />
                  <line x1="10" y1="10" x2="14" y2="14" />
                </svg>
                Search...
              </div>
              <button className="btn btn-primary" type="button" onClick={() => setPage("register")}>
                + New
              </button>
            </div>
          </div>
          <div className="content">
            <div className="section-header">
              <div className="filter-tabs">
                <div className="ftab active">All (2847)</div>
                <div className="ftab">Missing</div>
                <div className="ftab">Matched</div>
                <div className="ftab">Found</div>
              </div>
            </div>
            <div className="cases-grid">
              {allCases.map((item) => (
                <div className="case-card" key={item.name}>
                  <div className="case-img">
                    <AvatarFace />
                    <span className={`status-dot ${item.statusClass}`}>{item.status}</span>
                  </div>
                  <div className="case-body">
                    <div className="case-name">{item.name}</div>
                    <div className="case-meta">
                      {item.meta.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                    </div>
                    {item.confidence ? (
                      <div className="match-conf">
                        <div className="conf-bar">
                          <div className="conf-fill" style={{ width: `${item.confidence}%`, background: item.fill }} />
                        </div>
                        <span className="conf-text" style={{ color: item.fill }}>
                          {item.confidence}%
                        </span>
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (activePage === "found") {
      return (
        <div id="page-found" className="page-shell">
          <div className="topbar">
            <div className="page-title">Found Persons</div>
          </div>
          <div className="content">
            <div className="section-header">
              <div className="section-title" style={{ color: "var(--green)" }}>
                1,293 individuals reunited with families
              </div>
            </div>
            <div className="found-grid">
              {foundPeople.map((person) => (
                <div className="found-card" key={person.name}>
                  <div className="found-avatar">
                    <AvatarFace />
                  </div>
                  <div className="found-info">
                    <div className="found-name">{person.name}</div>
                    <div className="found-sub">{person.sub}</div>
                    <span className="reunited-badge">✓ Reunited</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (activePage === "admin") {
      return (
        <div id="page-admin" className="page-shell">
          <div className="topbar">
            <div className="page-title">Admin Panel</div>
            <span className="badge-admin" style={{ fontSize: 11, padding: "4px 10px" }}>
              ADMIN ONLY
            </span>
          </div>
          <div className="content">
            <div className="stats-row">
              <div className="stat-card">
                <div className="stat-label">Total Missing</div>
                <div className="stat-num" style={{ color: "var(--accent)" }}>
                  2,847
                </div>
                <div className="stat-delta">Active cases</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Total Found</div>
                <div className="stat-num" style={{ color: "var(--green)" }}>
                  1,293
                </div>
                <div className="stat-delta delta-up">▲ 34 this week</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Recovery Rate</div>
                <div className="stat-num" style={{ color: "var(--accent2)" }}>
                  45.4%
                </div>
                <div className="stat-delta delta-up">▲ 2.1% vs prior month</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Pending Review</div>
                <div className="stat-num" style={{ color: "var(--gold)" }}>
                  47
                </div>
                <div className="stat-delta">Matches need confirm</div>
              </div>
            </div>
            <div className="match-panel">
              <div className="match-title">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="var(--gold)">
                  <path d="M8 1l1.8 3.6L14 5.4l-3 2.9.7 4.1L8 10.3l-3.7 2.1.7-4.1-3-2.9 4.2-.8z" />
                </svg>
                Face Match Review — Top 3 Pending Confirmations
                <span className="match-title-badge">ADMIN</span>
              </div>
              <div className="match-row">
                {adminMatches.map((item) => (
                  <div className="match-item" key={item.name}>
                    <div className={`match-rank rank-${item.rank}`}>{item.rank}</div>
                    <div className="match-face">
                      <AvatarFace />
                    </div>
                    <div className="match-name">{item.name}</div>
                    <div className="pct-ring">
                      <Ring value={item.confidence} stroke={item.stroke} />
                      <div className="match-details">{item.details}</div>
                    </div>
                    <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
                      <button className="btn btn-primary" type="button" style={{ flex: 1, padding: 5, fontSize: 10 }}>
                        ✓ Confirm
                      </button>
                      <button className="btn btn-ghost" type="button" style={{ flex: 1, padding: 5, fontSize: 10 }}>
                        ✗ Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div id="page-dashboard" className="page-shell">
        <div className="page-tabs">
          <div className="ptab active">Overview</div>
          <div className="ptab">Recent Activity</div>
        </div>
        <div className="topbar">
          <div className="page-title">Dashboard</div>
          <div className="topbar-right">
            <div className="search-box">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="6.5" cy="6.5" r="4" />
                <line x1="10" y1="10" x2="14" y2="14" />
              </svg>
              Search cases...
            </div>
            <button className="btn btn-primary" type="button" onClick={() => setPage("register")}>
              + New Case
            </button>
          </div>
        </div>
        <div className="content">
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-label">Missing</div>
              <div className="stat-num">2,847</div>
              <div className="stat-delta delta-down">▲ 12 this week</div>
              <div className="stat-bar">
                <div className="stat-fill" style={{ width: "78%", background: "var(--accent)" }} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Found</div>
              <div className="stat-num">1,293</div>
              <div className="stat-delta delta-up">▲ 34 this week</div>
              <div className="stat-bar">
                <div className="stat-fill" style={{ width: "45%", background: "var(--green)" }} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Recovery Rate</div>
              <div className="stat-num">45.4%</div>
              <div className="stat-delta delta-up">▲ 2.1% vs last month</div>
              <div className="stat-bar">
                <div className="stat-fill" style={{ width: "45%", background: "var(--accent2)" }} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">AI Matches Made</div>
              <div className="stat-num">384</div>
              <div className="stat-delta delta-up">92% accuracy rate</div>
              <div className="stat-bar">
                <div className="stat-fill" style={{ width: "92%", background: "var(--gold)" }} />
              </div>
            </div>
          </div>

          <div className="match-panel">
            <div className="match-title">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="var(--gold)">
                <path d="M8 1l1.8 3.6L14 5.4l-3 2.9.7 4.1L8 10.3l-3.7 2.1.7-4.1-3-2.9 4.2-.8z" />
              </svg>
              Latest AI Face Matches
              <span className="match-title-badge">TOP 3</span>
            </div>
            <div className="match-row">
              {dashboardMatches.map((item) => (
                <div className="match-item" key={item.name}>
                  <div className={`match-rank rank-${item.rank}`}>{item.rank}</div>
                  <div className="match-face">
                    <AvatarFace />
                  </div>
                  <div className="match-name">{item.name}</div>
                  <div className="pct-ring">
                    <Ring value={item.confidence} stroke={item.stroke} />
                    <div className="match-details">{item.details}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="section-header">
            <div className="section-title">Recent Cases</div>
            <div className="filter-tabs">
              <div className="ftab active">All</div>
              <div className="ftab">Missing</div>
              <div className="ftab">Matched</div>
            </div>
          </div>
          <div className="cases-grid">
            {recentCases.map((item) => (
              <div className="case-card" key={item.name}>
                <div className="case-img">
                  <AvatarFace />
                  <span className={`status-dot ${item.statusClass}`}>{item.status}</span>
                </div>
                <div className="case-body">
                  <div className="case-name">{item.name}</div>
                  <div className="case-meta">
                    {item.meta.map((line) => (
                      <span key={line}>{line}</span>
                    ))}
                  </div>
                  {item.confidence ? (
                    <div className="match-conf">
                      <div className="conf-bar">
                        <div className="conf-fill" style={{ width: `${item.confidence}%`, background: item.fill }} />
                      </div>
                      <span className="conf-text" style={{ color: item.fill }}>
                        {item.confidence}%
                      </span>
                    </div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app" id="app">
      <div className="sidebar">
        <div className="logo">
          <div className="logo-title">Hope in Pixels</div>
          <div className="logo-sub">Missing Person Identification</div>
        </div>
        <nav>
          <div className="nav-section">Navigation</div>
          {navItems.map((item) => (
            <div
              key={item.id}
              className={page === item.id ? "nav-item active" : "nav-item"}
              onClick={() => setPage(item.id)}
            >
              {item.id === "dashboard" ? (
                <svg className="nav-icon" viewBox="0 0 16 16" fill="currentColor">
                  <rect x="1" y="1" width="6" height="6" rx="1.5" />
                  <rect x="9" y="1" width="6" height="6" rx="1.5" />
                  <rect x="1" y="9" width="6" height="6" rx="1.5" />
                  <rect x="9" y="9" width="6" height="6" rx="1.5" />
                </svg>
              ) : item.id === "register" ? (
                <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="8" cy="5" r="3" />
                  <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" />
                  <line x1="12" y1="7" x2="14" y2="7" />
                  <line x1="13" y1="6" x2="13" y2="8" />
                </svg>
              ) : item.id === "cases" ? (
                <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="2" y="2" width="12" height="12" rx="2" />
                  <line x1="5" y1="6" x2="11" y2="6" />
                  <line x1="5" y1="9" x2="9" y2="9" />
                </svg>
              ) : item.id === "found" ? (
                <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M3 8l4 4 6-6" />
                </svg>
              ) : (
                <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="8" cy="8" r="5" />
                  <path d="M8 5v3l2 2" />
                </svg>
              )}
              {item.label}
            </div>
          ))}
        </nav>
        <div className="user-area">
          <AuthPanel currentUser={currentUser} onLogin={handleLogin} onRegister={handleRegister} onLogout={handleLogout} />
        </div>
      </div>

      <div className="main" id="main-area">
        {renderPage()}
      </div>

      <div className="chatbot-btn" onClick={openChatReply}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
        </svg>
      </div>

      <div className={chatOpen ? "chat-panel open" : "chat-panel"} id="chat-panel">
        <div className="chat-head">
          <div className="chat-indicator" />
          <div>
            <div className="chat-head-title">Hope Assistant</div>
            <div className="chat-head-sub">AI-powered FAQ</div>
          </div>
        </div>
        <div className="chat-messages" id="chat-msgs">
          {chatMessages.map((message, index) => (
            <div key={`${message.type}-${index}-${message.text.slice(0, 10)}`} className={`msg msg-${message.type}`}>
              {message.text}
            </div>
          ))}
        </div>
        <div className="chat-input-area">
          <input
            className="chat-input"
            id="chat-in"
            placeholder="Ask anything..."
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                sendChat();
              }
            }}
          />
          <button className="chat-send" type="button" onClick={sendChat}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
