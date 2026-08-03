import { useState } from "react";
import { autoCategorizeAll } from "../api/transactions";

export default function AutoCategorizeButton({ onDone }) {
  const [running, setRunning] = useState(false);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  async function handleClick() {
    setRunning(true);
    setError("");
    setSummary(null);
    try {
      const result = await autoCategorizeAll();
      setSummary(result);
      await onDone();
    } catch (err) {
      setError(err.response?.data?.detail || "Auto-categorization failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="auto-categorize">
      <button type="button" className="secondary-button" onClick={handleClick} disabled={running}>
        {running ? "Categorizing..." : "Auto-categorize with AI"}
      </button>
      {error && <p className="error">{error}</p>}
      {summary && (
        <p className="csv-result">
          {summary.total_uncategorized === 0
            ? "No uncategorized transactions."
            : `Categorized ${summary.applied} of ${summary.total_uncategorized}` +
              (summary.low_confidence_skipped > 0
                ? ` (${summary.low_confidence_skipped} left for you — the model wasn't confident enough).`
                : ".")}
        </p>
      )}
    </div>
  );
}