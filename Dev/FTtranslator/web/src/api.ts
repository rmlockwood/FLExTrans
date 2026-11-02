// The FTtranslator server's API (fttranslator/server.py) and the shapes it answers with.
//
// RunRecord mirrors pipeline.RunResult: its field names are the keys of the run record JSON, so a change there must be made here too.

export interface ApprovedWord {
  word: string;
  location: string;
  analysis: string;
  basis: string;
}

export interface Message {
  level: "info" | "warning" | "error";
  message: string;
  ref: string | null;
}

export interface StepTiming {
  step: string;
  seconds: number;
}

export interface RunRecord {
  title: string | null;
  source: string;
  translation: string | null;
  ok: boolean;
  steps: string[];
  approved: ApprovedWord[];
  unparsed: string[];
  unanalysed: string[];
  untranslated: string[];
  unsynthesized: string[];
  messages: Message[];
  timings: StepTiming[];
  totalSeconds: number | null;
}

export interface Status {
  workProject: string;
  sourceProject: string;
  targetProject: string;
  projectsOpen: boolean;
  translationCount: number;
}

export interface TranslateOptions {
  insert: boolean;
  keepApprovals: boolean;
}

// The server answers errors as {error: message}; turn those (and a server that isn't there) into an Error with a readable message
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(path, init);
  } catch {
    throw new Error("Can't reach the FTtranslator server. Is 'python -m fttranslator serve' still running?");
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(body?.error ?? `The server answered ${response.status} ${response.statusText}`);
  }

  return body as T;
}

export function getStatus(): Promise<Status> {
  return request<Status>("/api/status");
}

export async function getRuns(limit = 50): Promise<RunRecord[]> {
  const body = await request<{ runs: RunRecord[] }>(`/api/runs?limit=${limit}`);
  return body.runs;
}

// JSON content type is required by the server: it is what stops other web pages from posting to it (see SAFETY in server.py)
export async function translate(text: string, options: TranslateOptions): Promise<RunRecord> {
  const body = await request<{ result: RunRecord; record: string | null }>("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, ...options }),
  });

  return body.result;
}
