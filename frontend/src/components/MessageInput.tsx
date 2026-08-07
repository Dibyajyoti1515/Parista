import { useState, type FormEvent } from "react";

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

/**
 * The message input — a text field and send button. Submits on Enter or
 * button click, and is disabled while a request is in flight.
 */
export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        className="message-input__field"
        type="text"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Describe your conflict…"
        disabled={disabled}
        aria-label="Describe your conflict"
      />
      <button
        className="message-input__send"
        type="submit"
        disabled={disabled || !text.trim()}
      >
        Send
      </button>
    </form>
  );
}