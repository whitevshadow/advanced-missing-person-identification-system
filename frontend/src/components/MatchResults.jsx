import FeedbackPanel from "./FeedbackPanel";

function decisionClass(decision) {
  if (decision === "strong_match") return "strong";
  if (decision === "possible_match") return "possible";
  return "none";
}

export default function MatchResults({ matches, latestSightingResult, onFeedback }) {
  return (
    <section>
      <h2>Match Results</h2>

      {latestSightingResult?.message && (
        <p className="meta">Latest sighting: {latestSightingResult.message}</p>
      )}

      {matches.length === 0 ? (
        <p className="meta">No match records yet.</p>
      ) : (
        <div className="card-list">
          {matches.map((match) => (
            <article className="card" key={match.id}>
              <h3>{match.missing_person_name}</h3>
              <p>
                <span className={`tag ${decisionClass(match.decision)}`}>
                  {match.decision}
                </span>
                Confidence: {match.confidence_percent}%
              </p>
              <p className="meta">Location: {match.current_city}</p>
              <p className="meta">Description: {match.description || "N/A"}</p>
              <ul>
                {(match.reasoning || []).map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <FeedbackPanel
                matchId={match.id}
                currentFeedback={match.user_feedback}
                onSubmit={onFeedback}
              />
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
