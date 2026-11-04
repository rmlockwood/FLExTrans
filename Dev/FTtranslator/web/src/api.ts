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
  // Sent only by the offline server: the bundle the text was translated with
  bundle?: string;
}

// One of the offline server's bundles (GET /api/bundles); id is what requests name it by
export interface BundleInfo {
  id: string;
  workProject: string;
  sourceProject: string;
  targetProject: string;
  created: string;
}

export interface Status {
  workProject: string;
  sourceProject: string;
  targetProject: string;
  projectsOpen: boolean;
  translationCount: number;
  // Sent only by the offline server (offlineserver.py), which translates from a bundle with no FLEx projects; bundle is the one this status is for
  offline?: boolean;
  bundle?: string;
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

// The bundle a request is for, as a query parameter; the desktop server ignores it, and the offline server uses its default bundle without one
function bundleQuery(bundle: string | null, separator: "?" | "&"): string {
  return bundle ? `${separator}bundle=${encodeURIComponent(bundle)}` : "";
}

export function getStatus(bundle: string | null = null): Promise<Status> {
  return request<Status>(`/api/status${bundleQuery(bundle, "?")}`);
}

export async function getRuns(limit = 50, bundle: string | null = null): Promise<RunRecord[]> {
  const body = await request<{ runs: RunRecord[] }>(`/api/runs?limit=${limit}${bundleQuery(bundle, "&")}`);
  return body.runs;
}

// Only the offline server has bundles
export async function getBundles(): Promise<{ bundles: BundleInfo[]; default: string | null }> {
  return request<{ bundles: BundleInfo[]; default: string | null }>("/api/bundles");
}

// JSON content type is required by the server: it is what stops other web pages from posting to it (see SAFETY in server.py)
export async function translate(text: string, options: TranslateOptions, bundle: string | null = null): Promise<RunRecord> {
  const body = await request<{ result: RunRecord; record: string | null }>("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bundle ? { text, ...options, bundle } : { text, ...options }),
  });

  return body.result;
}
