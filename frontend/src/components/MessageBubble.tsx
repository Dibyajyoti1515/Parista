import type { AnalyzeResponse } from "../api/client";
import { StructuredResponse } from "./StructuredResponse";

export interface ChatMessage {
  id: string;
  role: "user" | "agent";
  content: string;
  /** Present on agent messages that carry a structured analysis. */
  response?: AnalyzeResponse;
}

interface MessageBubbleProps {
  message: ChatMessage;
}

/**
 * A single message in the conversation. User messages render as plain text;
 * agent messages render the structured analysis card when available.
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`message message--${message.role}`}>
      <div className="message__bubble">
        {isUser ? (
          <p className="message__text">{message.content}</p>
        ) : message.response ? (
          <StructuredResponse response={message.response} />
        ) : (
          <p className="message__text">{message.content}</p>
        )}
      </div>
    </div>
  );
}