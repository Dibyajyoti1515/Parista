import { useEffect, useRef } from "react";
import { MessageBubble, type ChatMessage } from "./MessageBubble";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

/**
 * The conversation view — a scrollable list of user and agent messages.
 * Auto-scrolls to the newest message as the conversation grows.
 */
export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="message-list">
      {messages.length === 0 && !isLoading && (
        <div className="message-list__empty">
          <p>Describe an interpersonal conflict and I'll provide a grounded, cited analysis.</p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="message message--agent">
          <div className="message__bubble message__bubble--loading">
            <span className="typing-indicator">
              <span />
              <span />
              <span />
            </span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}