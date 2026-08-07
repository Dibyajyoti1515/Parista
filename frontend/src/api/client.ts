/**
 * Parista API client.
 *
 * Types and functions for talking to the backend HTTP API, matching the
 * contract in specs/001-grounded-conflict-assistant/contracts/api.md.
 *
 * The backend `/api/analyze` endpoint may not be implemented yet, so this
 * client supports a mock mode (VITE_USE_MOCK=1, the default) that returns a
 * realistic response matching the contract schema. Set VITE_USE_MOCK=0 to
 * call the real backend through the Vite dev proxy (`/api` -> localhost:8000).
 */

export type Domain = "romantic" | "family" | "workplace" | "general";
export type Tone = "casual" | "formal" | "playful" | "serious";

export interface Classification {
  domain: Domain;
  conflict_type: string;
  emotional_tone: string;
}

export interface Source {
  source_title: string;
  framework_name: string;
  source_url?: string;
}

export interface Analysis {
  psychological_pattern: string;
  explanation: string;
  source: Source;
}

export interface SuggestedReply {
  text: string;
  tone: Tone;
}

/** Normal / supplementary response shape. */
export interface AnalyzeResponse {
  conversation_id: string;
  classification: Classification;
  analysis: Analysis | null;
  suggested_reply?: SuggestedReply;
  supplementary: boolean;
  /** Present only on the crisis-override variant. */
  crisis_override?: boolean;
  /** Present only on the insufficient-grounded-info / crisis variants. */
  message?: string;
}

const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "1") !== "0";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** A realistic mocked response matching the contract schema. */
function mockAnalyzeResponse(text: string): AnalyzeResponse {
  const lower = text.toLowerCase();
  const isCrisis =
    lower.includes("hurt myself") ||
    lower.includes("kill myself") ||
    lower.includes("self harm") ||
    lower.includes("suicide");

  if (isCrisis) {
    return {
      conversation_id: "mock-crisis-conversation",
      classification: {
        domain: "general",
        conflict_type: "crisis",
        emotional_tone: "distressed",
      },
      analysis: null,
      supplementary: false,
      crisis_override: true,
      message:
        "I'm really glad you reached out. What you're feeling matters, and you don't have to go through it alone. Please consider reaching out to a trusted person or a support line — you deserve support right now. (This is a supportive message, not relationship advice.)",
    };
  }

  const isWorkplace = lower.includes("work") || lower.includes("boss") || lower.includes("colleague");
  const isFamily = lower.includes("family") || lower.includes("mom") || lower.includes("dad") || lower.includes("parent");
  const domain: Domain = isWorkplace ? "workplace" : isFamily ? "family" : "romantic";

  return {
    conversation_id: "mock-conversation-1234",
    classification: {
      domain,
      conflict_type: "recurring misunderstanding",
      emotional_tone: "frustrated",
    },
    analysis: {
      psychological_pattern: "Rejection Sensitivity",
      explanation:
        "This pattern describes a tendency to anxiously expect, readily perceive, and overreact to perceived rejection. In recurring conflicts where one partner feels unheard, the underlying fear of being dismissed can amplify the emotional response, making the same issue resurface again and again.",
      source: {
        source_title: "Downey & Feldman 1996",
        framework_name: "Rejection Sensitivity",
        source_url: "https://doi.org/10.1037/0022-3514.70.6.1327",
      },
    },
    suggested_reply: {
      text: "I want to talk about this because it matters to me. When I bring it up and it feels like it's not landing, I start to feel like I'm not being heard — and that's hard. Can we slow down and make sure we're both really listening?",
      tone: "casual",
    },
    supplementary: false,
  };
}

/**
 * Analyze a text description of an interpersonal conflict.
 *
 * In mock mode (default) this returns a contract-shaped response without
 * hitting the network. Otherwise it POSTs to `/api/analyze`.
 */
export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  if (USE_MOCK) {
    await delay(900); // simulate network latency
    return mockAnalyzeResponse(text);
  }

  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as AnalyzeResponse;
}