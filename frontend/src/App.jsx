import { useCallback, useEffect, useState } from "react";

import {
  fetchAlerts,
  fetchMatches,
  fetchMissingPersons,
  registerMissingPerson,
  reportSighting,
  submitFeedback,
} from "./api";
import AlertHistory from "./components/AlertHistory";
import MatchResults from "./components/MatchResults";
import MissingPersonForm from "./components/MissingPersonForm";
import MissingPersonsList from "./components/MissingPersonsList";
import SightingForm from "./components/SightingForm";

function extractError(error) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item?.msg) return item.msg;
        return JSON.stringify(item);
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(" | ");
    }
  }

  if (detail && typeof detail === "object") {
    try {
      return JSON.stringify(detail);
    } catch {
      return "Request failed";
    }
  }

  return error?.message || "Request failed";
}

export default function App() {
  const [missingPersons, setMissingPersons] = useState([]);
  const [matches, setMatches] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [latestSightingResult, setLatestSightingResult] = useState(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const refreshDashboard = useCallback(async () => {
    try {
      const [persons, matchRows, alertRows] = await Promise.all([
        fetchMissingPersons(),
        fetchMatches(),
        fetchAlerts(),
      ]);
      setMissingPersons(persons);
      setMatches(matchRows);
      setAlerts(alertRows);
    } catch (err) {
      setError(extractError(err));
    }
  }, []);

  useEffect(() => {
    refreshDashboard();
  }, [refreshDashboard]);

  const handleMissingPersonSubmit = async (payload) => {
    setError("");
    setNotice("Registering missing person...");

    try {
      await registerMissingPerson(payload);
      setNotice("Missing person registered successfully.");
      await refreshDashboard();
    } catch (err) {
      setError(extractError(err));
      setNotice("");
    }
  };

  const handleSightingSubmit = async (payload) => {
    setError("");
    setNotice("Running intelligent match pipeline...");

    try {
      const response = await reportSighting(payload);
      setLatestSightingResult(response);
      setNotice("Sighting processed.");
      await refreshDashboard();
    } catch (err) {
      setError(extractError(err));
      setNotice("");
    }
  };

  const handleFeedback = async ({ matchId, accepted, comments }) => {
    setError("");

    try {
      await submitFeedback({ match_id: matchId, accepted, comments });
      setNotice("Feedback stored.");
      await refreshDashboard();
    } catch (err) {
      setError(extractError(err));
    }
  };

  return (
    <main className="app-container">
      <header className="top-header">
        <h1>Advanced Missing Person Identification System</h1>
        <p>
          Pre-trained deep learning face recognition + contextual filtering +
          real-time alert history
        </p>
      </header>

      {notice && <p className="notice-banner">{notice}</p>}
      {error && <p className="error-banner">{error}</p>}

      <section className="grid two-cols">
        <article className="panel">
          <MissingPersonForm onSubmit={handleMissingPersonSubmit} />
        </article>
        <article className="panel">
          <SightingForm onSubmit={handleSightingSubmit} />
        </article>
      </section>

      <section className="grid two-cols">
        <article className="panel">
          <MissingPersonsList persons={missingPersons} />
        </article>
        <article className="panel">
          <MatchResults
            latestSightingResult={latestSightingResult}
            matches={matches}
            onFeedback={handleFeedback}
          />
        </article>
      </section>

      <section className="panel">
        <AlertHistory alerts={alerts} />
      </section>
    </main>
  );
}
