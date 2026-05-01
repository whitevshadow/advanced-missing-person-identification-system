import { useState } from "react";

export default function FeedbackPanel({ matchId, currentFeedback, onSubmit }) {
  const [comments, setComments] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (currentFeedback) {
    return <p className="meta">Feedback recorded: {currentFeedback}</p>;
  }

  const handleAction = async (accepted) => {
    setIsSubmitting(true);
    try {
      await onSubmit({ matchId, accepted, comments });
      setComments("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <label className="field">
        <span>Feedback comments (optional)</span>
        <input
          value={comments}
          onChange={(event) => setComments(event.target.value)}
          placeholder="Any validation notes"
        />
      </label>
      <button disabled={isSubmitting} onClick={() => handleAction(true)} type="button">
        Accept Match
      </button>{" "}
      <button
        className="ghost"
        disabled={isSubmitting}
        onClick={() => handleAction(false)}
        type="button"
      >
        Reject Match
      </button>
    </div>
  );
}
