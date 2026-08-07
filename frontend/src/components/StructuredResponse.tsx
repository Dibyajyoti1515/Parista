import type { AnalyzeResponse } from "../api/client";

interface StructuredResponseProps {
  response: AnalyzeResponse;
}

/**
 * Renders the structured analysis returned by the backend, handling the
 * normal, supplementary, crisis-override, and insufficient-grounded-info
 * variants of the contract response schema.
 */
export function StructuredResponse({ response }: StructuredResponseProps) {
  // Crisis override variant
  if (response.crisis_override) {
    return (
      <div className="structured-response structured-response--crisis">
        <div className="structured-response__badge">Crisis support</div>
        <p className="structured-response__message">{response.message}</p>
      </div>
    );
  }

  // Insufficient grounded information variant
  if (!response.analysis) {
    return (
      <div className="structured-response structured-response--fallback">
        <div className="structured-response__badge">No grounded answer</div>
        <p className="structured-response__message">
          {response.message ?? "insufficient grounded information"}
        </p>
      </div>
    );
  }

  const { classification, analysis, suggested_reply, supplementary } = response;

  return (
    <div className="structured-response">
      {supplementary && (
        <div className="structured-response__badge structured-response__badge--supplementary">
          Supplementary source
        </div>
      )}

      <div className="structured-response__classification">
        <span className="tag">{classification.domain}</span>
        <span className="tag">{classification.conflict_type}</span>
        <span className="tag">{classification.emotional_tone}</span>
      </div>

      <div className="structured-response__section">
        <h4 className="structured-response__label">Pattern</h4>
        <p className="structured-response__pattern">{analysis.psychological_pattern}</p>
      </div>

      <div className="structured-response__section">
        <h4 className="structured-response__label">Explanation</h4>
        <p className="structured-response__explanation">{analysis.explanation}</p>
      </div>

      <div className="structured-response__section">
        <h4 className="structured-response__label">Source</h4>
        <p className="structured-response__source">
          {analysis.source.source_title}
          {analysis.source.framework_name && (
            <span className="structured-response__framework">
              {" "}
              — {analysis.source.framework_name}
            </span>
          )}
          {analysis.source.source_url && (
            <>
              {" "}
              (
              <a
                href={analysis.source.source_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                link
              </a>
              )
            </>
          )}
        </p>
      </div>

      {suggested_reply && (
        <div className="structured-response__section structured-response__section--reply">
          <h4 className="structured-response__label">
            Suggested reply{" "}
            <span className="structured-response__tone">({suggested_reply.tone})</span>
          </h4>
          <p className="structured-response__reply">{suggested_reply.text}</p>
        </div>
      )}
    </div>
  );
}