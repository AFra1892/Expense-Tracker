import { useRef, useState } from "react";
import { importTransactionsCsv } from "../api/transactions";

export default function CsvImport({ onImported }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError("");
    setResult(null);
    try {
      const res = await importTransactionsCsv(file);
      setResult(res);
      await onImported();
    } catch (err) {
      setError(err.response?.data?.detail || "Import failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div className="csv-import">
      <button type="button" className="secondary-button" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
        {uploading ? "Importing..." : "Import CSV"}
      </button>
      <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} style={{ display: "none" }} />
      <span className="csv-hint">Columns: date, description, amount, category (optional)</span>

      {error && <p className="error">{error}</p>}
      {result && (
        <p className="csv-result">
          Imported {result.imported} transaction{result.imported === 1 ? "" : "s"}
          {result.skipped > 0 && `, skipped ${result.skipped} row${result.skipped === 1 ? "" : "s"}`}.
          {result.errors.length > 0 && (
            <details>
              <summary>View errors</summary>
              <ul>
                {result.errors.map((e, i) => (
                  <li key={i}>Row {e.row}: {e.error}</li>
                ))}
              </ul>
            </details>
          )}
        </p>
      )}
    </div>
  );
}