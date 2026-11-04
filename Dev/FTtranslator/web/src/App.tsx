// The FTtranslator page: type a sentence, press Enter, get its translation - the interactive command in a browser.
//
// The server keeps the FLEx projects open between translations, so only the first one is slow (it opens the projects). Translations from this session are listed newest first under the box;
// the Saved runs tab lists the run records saved in the work project, including those from the command line. The server answers one translation at a time, so the Translate button is
// disabled while one is running, but the box stays editable. The text stays in the box after translating, so a sentence can be tweaked and translated again.
//
// The offline server (offlineserver.py) can hold several bundles. Then the header has a drop-down to choose one, the choice is remembered in this browser, and every request names it; the
// Saved runs tab shows the chosen bundle's runs. The desktop server has no /api/bundles, so the drop-down never shows there.

import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";

import { getBundles, getRuns, getStatus, translate } from "./api";
import type { BundleInfo, RunRecord, Status, TranslateOptions } from "./api";
import ResultCard from "./ResultCard";

// Where this browser remembers the chosen bundle. Storage can be missing or blocked (private windows), so every use is guarded and the page works without it.
const BUNDLE_KEY = "fttranslator.bundle";

function storedBundle(): string | null {
  try {
    return window.localStorage.getItem(BUNDLE_KEY);
  } catch {
    return null;
  }
}

function storeBundle(bundle: string) {
  try {
    window.localStorage.setItem(BUNDLE_KEY, bundle);
  } catch {
    // Not remembered; the server's default is used next time
  }
}

// A translation of this session: the record, or the error that stopped it
interface SessionEntry {
  id: number;
  source: string;
  record?: RunRecord;
  error?: string;
}

type Tab = "session" | "saved";

export default function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [options, setOptions] = useState<TranslateOptions>({ insert: false, keepApprovals: false });
  const [busy, setBusy] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [entries, setEntries] = useState<SessionEntry[]>([]);
  const [tab, setTab] = useState<Tab>("session");
  const [savedRuns, setSavedRuns] = useState<RunRecord[] | null>(null);
  const [savedError, setSavedError] = useState<string | null>(null);
  const [bundles, setBundles] = useState<BundleInfo[]>([]);
  const [bundle, setBundle] = useState<string | null>(null);
  const textBox = useRef<HTMLTextAreaElement>(null);
  const nextId = useRef(1);

  function refreshStatus(forBundle: string | null = bundle) {
    getStatus(forBundle)
      .then((newStatus) => {
        setStatus(newStatus);
        setStatusError(null);
      })
      .catch((error: Error) => setStatusError(error.message));
  }

  // Find out whether the server has bundles, and pick the remembered one if it is still there, else the server's default. A server without /api/bundles is the desktop one.
  useEffect(() => {
    getBundles()
      .then((answer) => {
        const remembered = storedBundle();
        const chosen = answer.bundles.some((info) => info.id === remembered) ? remembered : answer.default;
        setBundles(answer.bundles);
        setBundle(chosen);
        refreshStatus(chosen);
      })
      .catch(() => refreshStatus(null));
  }, []);

  function chooseBundle(newBundle: string) {
    setBundle(newBundle);
    storeBundle(newBundle);
    setStatus(null);
    refreshStatus(newBundle);
  }

  // Count the seconds while a translation runs, so a slow first one visibly isn't stuck
  useEffect(() => {
    if (!busy) {
      return;
    }

    const started = Date.now();
    setElapsed(0);
    const timer = window.setInterval(() => setElapsed((Date.now() - started) / 1000), 100);

    return () => window.clearInterval(timer);
  }, [busy]);

  // The saved runs are fetched each time the tab is opened, so they include this session's
  useEffect(() => {
    if (tab !== "saved") {
      return;
    }

    setSavedError(null);
    setSavedRuns(null);
    getRuns(50, bundle)
      .then(setSavedRuns)
      .catch((error: Error) => setSavedError(error.message));
  }, [tab, bundle]);

  async function submit() {
    const source = text.trim();

    if (!source || busy) {
      return;
    }

    const id = nextId.current++;
    setBusy(true);
    setTab("session");

    // The text stays in the box, so it can be adjusted and translated again
    try {
      const record = await translate(source, options, bundle);
      setEntries((current) => [{ id, source, record }, ...current]);
    } catch (error) {
      setEntries((current) => [{ id, source, error: (error as Error).message }, ...current]);
    } finally {
      setBusy(false);
      refreshStatus();
      textBox.current?.focus();
    }
  }

  // Enter translates; Shift+Enter starts a new line (each line becomes a paragraph of the text)
  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <div className="page">
      <header className="top">
        <div>
          <h1>FTtranslator</h1>
          {status && (
            <div className="projects">
              {bundles.length > 1 && bundle ? (
                <select className="bundle-select" value={bundle} onChange={(event) => chooseBundle(event.target.value)} disabled={busy} title="The bundle to translate with">
                  {bundles.map((info) => (
                    <option key={info.id} value={info.id}>
                      {info.id}
                    </option>
                  ))}
                </select>
              ) : (
                <span title="Work project">{status.workProject}</span>
              )}
              <span className="muted">
                {" "}
                · {status.sourceProject} → {status.targetProject || "(no target project)"}
              </span>
            </div>
          )}
        </div>
        <StatusPill status={status} error={statusError} busy={busy} />
      </header>

      <section className="composer">
        <textarea
          ref={textBox}
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a sentence and press Enter"
          dir="auto"
          rows={3}
          autoFocus
        />
        <div className="composer-bar">
          {/* The offline server has no FLEx projects to insert into or keep approvals in, so these options only show for the desktop server. They wait for the status so they don't flash up first. */}
          {status && !status.offline && (
            <>
              <label title="Also put the translation into the target project (Insert Target Text)">
                <input type="checkbox" checked={options.insert} onChange={(event) => setOptions({ ...options, insert: event.target.checked })} /> Insert into target project
              </label>
              <label title="Leave the guessed analyses approved in the source text, so they count for future guesses. Normally they are released for review in FLEx.">
                <input type="checkbox" checked={options.keepApprovals} onChange={(event) => setOptions({ ...options, keepApprovals: event.target.checked })} /> Keep approvals
              </label>
            </>
          )}
          <span className="spacer" />
          <span className="muted small">Shift+Enter for a new line</span>
          <button className="primary" onClick={submit} disabled={busy || !text.trim()}>
            {busy ? `Translating… ${elapsed.toFixed(1)} s` : "Translate"}
          </button>
        </div>
      </section>

      <nav className="tabs">
        <button className={tab === "session" ? "tab active" : "tab"} onClick={() => setTab("session")}>
          This session{entries.length > 0 ? ` (${entries.length})` : ""}
        </button>
        <button className={tab === "saved" ? "tab active" : "tab"} onClick={() => setTab("saved")}>
          Saved runs
        </button>
      </nav>

      {tab === "session" && (
        <section className="results">
          {entries.length === 0 && !busy && <p className="muted empty">Translations will appear here, newest first.</p>}
          {busy && (
            <div className="card pending">
              Translating
              {status && !status.projectsOpen ? (status.offline ? " — loading the bundle for its first translation, which takes a few seconds" : " — opening the projects for the first translation, which takes a few seconds") : ""}…
            </div>
          )}
          {entries.map((entry) =>
            entry.record ? (
              <ResultCard key={entry.id} record={entry.record} />
            ) : (
              <article key={entry.id} className="card card-failed">
                <div className="source" dir="auto">
                  {entry.source}
                </div>
                <div className="error-text">{entry.error}</div>
              </article>
            ),
          )}
        </section>
      )}

      {tab === "saved" && (
        <section className="results">
          {savedError && <div className="card card-failed error-text">{savedError}</div>}
          {!savedError && savedRuns === null && <p className="muted empty">Loading…</p>}
          {savedRuns?.length === 0 && <p className="muted empty">No saved runs yet.</p>}
          {savedRuns?.map((record, index) => <ResultCard key={`${record.title}-${index}`} record={record} showTitle />)}
        </section>
      )}
    </div>
  );
}

function StatusPill({ status, error, busy }: { status: Status | null; error: string | null; busy: boolean }) {
  if (error) {
    return (
      <span className="pill pill-error" title={error}>
        Server not reachable
      </span>
    );
  }

  if (!status) {
    return <span className="pill">Connecting…</span>;
  }

  if (busy) {
    return <span className="pill pill-busy">Translating</span>;
  }

  if (status.projectsOpen) {
    return (
      <span className="pill pill-ok" title={status.offline ? "The bundle is loaded" : "The projects are open, so each translation takes about half a second"}>
        Ready · {status.translationCount} translated
      </span>
    );
  }

  return status.offline ? (
    <span className="pill" title="The first translation with this bundle loads it, which takes a few seconds">
      Ready · bundle loads on first translation
    </span>
  ) : (
    <span className="pill" title="The first translation opens the FLEx projects, which takes a few seconds">
      Ready · projects open on first translation
    </span>
  );
}
