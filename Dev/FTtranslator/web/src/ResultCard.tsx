// One translation: the source, the translation, the words that failed and why, and - folded away - the analyses chosen, the messages and the step times.
//
// Used for this session's translations and for the saved runs alike, since both are run records. Text in the vernacular gets dir="auto" so a right-to-left target (Arabic script, Hebrew)
// displays the right way round without knowing the language in advance.

import { useState } from "react";

import type { RunRecord } from "./api";

// The run record's lists of failed words, with the label the command line also uses
const PROBLEM_GROUPS: { key: keyof RunRecord; label: string; hint: string }[] = [
  { key: "unparsed", label: "No parse", hint: "HermitCrab found no parse for these words" },
  { key: "unanalysed", label: "No analysis", hint: "These words were left without an analysis, so FLExTrans treated them as unknown" },
  { key: "untranslated", label: "Not linked", hint: "These source senses have no link to a target sense" },
  { key: "unsynthesized", label: "Not synthesized", hint: "The synthesizer couldn't produce these target words" },
];

function unique(words: string[]): string[] {
  return Array.from(new Set(words));
}

function formatSeconds(seconds: number): string {
  return seconds < 10 ? `${seconds.toFixed(2)} s` : `${seconds.toFixed(1)} s`;
}

interface Props {
  record: RunRecord;
  showTitle?: boolean;
}

export default function ResultCard({ record, showTitle = false }: Props) {
  const [copied, setCopied] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  // Each paragraph of the translation on its own line, with the synthesizer's extra spacing tidied up
  const translationLines = (record.translation ?? "").split("\n").map((line) => line.split(/\s+/).filter(Boolean).join(" ")).filter(Boolean);
  const problems = PROBLEM_GROUPS.map((group) => ({ ...group, words: unique(record[group.key] as string[]) })).filter((group) => group.words.length > 0);
  const notices = record.messages.filter((message) => message.level !== "info");
  const shownMessages = showInfo ? record.messages : notices;

  async function copyTranslation() {
    await navigator.clipboard.writeText(translationLines.join("\n"));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  return (
    <article className={`card ${record.ok ? "" : "card-failed"}`}>
      <header className="card-header">
        <div className="source" dir="auto">
          {record.source.trim()}
        </div>
        <div className="card-meta">
          {record.totalSeconds !== null && <span className="muted">{formatSeconds(record.totalSeconds)}</span>}
          <span className={`badge ${record.ok ? "badge-ok" : "badge-failed"}`}>{record.ok ? "OK" : `Failed after ${record.steps[record.steps.length - 1] ?? "start"}`}</span>
        </div>
      </header>

      {translationLines.length > 0 && (
        <div className="translation-row">
          <div className="translation" dir="auto">
            {translationLines.map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
          <button className="ghost" onClick={copyTranslation} title="Copy the translation">
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      )}

      {problems.length > 0 && (
        <div className="problems">
          {problems.map((group) => (
            <div key={group.key} className="problem-group" title={group.hint}>
              <span className="problem-label">{group.label}</span>
              {group.words.map((word) => (
                <span key={word} className="chip" dir="auto">
                  {word}
                </span>
              ))}
            </div>
          ))}
        </div>
      )}

      {showTitle && record.title && <div className="muted small">Source text in FLEx: {record.title}</div>}

      <div className="details-row">
        {record.approved.length > 0 && (
          <details>
            <summary>Analyses chosen ({record.approved.length})</summary>
            <table>
              <thead>
                <tr>
                  <th>Word</th>
                  <th>Analysis</th>
                  <th>Why</th>
                </tr>
              </thead>
              <tbody>
                {record.approved.map((approved) => (
                  <tr key={approved.location}>
                    <td dir="auto">{approved.word}</td>
                    <td dir="auto">{approved.analysis}</td>
                    <td className="muted">{approved.basis}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        )}

        {record.messages.length > 0 && (
          <details open={notices.some((message) => message.level === "error")}>
            <summary>
              Messages{notices.length > 0 ? ` (${notices.length} warning${notices.length === 1 ? "" : "s"} or error${notices.length === 1 ? "" : "s"})` : ""}
            </summary>
            <label className="small muted">
              <input type="checkbox" checked={showInfo} onChange={(event) => setShowInfo(event.target.checked)} /> Show all messages
            </label>
            <ul className="messages">
              {shownMessages.map((message, index) => (
                <li key={index} className={`message-${message.level}`} dir="auto">
                  {message.message}
                </li>
              ))}
              {shownMessages.length === 0 && <li className="muted">No warnings or errors.</li>}
            </ul>
          </details>
        )}

        {record.timings.length > 0 && <StepTimes record={record} />}
      </div>
    </article>
  );
}

// Each step's time as a bar, then the time outside the steps (opening the source project on the first run, and saving) and the total
function StepTimes({ record }: { record: RunRecord }) {
  const longest = Math.max(...record.timings.map((timing) => timing.seconds), 0.001);
  const stepTotal = record.timings.reduce((sum, timing) => sum + timing.seconds, 0);

  return (
    <details>
      <summary>Step times</summary>
      <table className="timings">
        <tbody>
          {record.timings.map((timing) => (
            <tr key={timing.step}>
              <td>{timing.step}</td>
              <td className="bar-cell">
                <span className="bar" style={{ width: `${(timing.seconds / longest) * 100}%` }} />
              </td>
              <td className="number">{formatSeconds(timing.seconds)}</td>
            </tr>
          ))}
          {record.totalSeconds !== null && (
            <>
              <tr>
                <td>Outside the steps (open, save)</td>
                <td />
                <td className="number">{formatSeconds(Math.max(record.totalSeconds - stepTotal, 0))}</td>
              </tr>
              <tr className="total">
                <td>Total</td>
                <td />
                <td className="number">{formatSeconds(record.totalSeconds)}</td>
              </tr>
            </>
          )}
        </tbody>
      </table>
    </details>
  );
}
