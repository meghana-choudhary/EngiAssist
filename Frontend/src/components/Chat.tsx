import { useState, useCallback, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import { performSearch } from "../util/Util.ts";

interface Message {
  text: string;
  sender: "user" | "bot";
}

interface Props {
  returnOptions: (options: any) => void; // Specify function type
}

// Move constants outside the component
const GENRE_OPTIONS = [
  { label: "All", value: "All" },
  { label: "Finance", value: "Finance" },
  { label: "Economics", value: "Economics" },
  { label: "Lab Manual", value: "Lab Manual" },
  { label: "Architecture", value: "Architecture" },
  { label: "Mechanical", value: "Mechanical" },
  { label: "IOT", value: "IOT" },
  { label: "Comic", value: "Comic" },
  { label: "Story", value: "Story" },
  { label: "Poem", value: "Poem" },
];

const MODEL_OPTIONS = [
  { label: "Gemma", value: "gemma3:27b" },
  { label: "Llama 3.3", value: "llama-3.3-70b-versatile" },
  { label: "Gemini", value: "gemini-2.5-pro-exp-03-25" },
  { label: "Open AI", value: "gpt-4o" },
];

const DEFAULT_MODEL = MODEL_OPTIONS[0].value;

const Chat = ({ returnOptions }: Props) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null); // Use null for no selection
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [sendPressed, setSendPressed] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [apiKey, setApiKey] = useState(""); // Default to empty string
  const [searchWeb, setSearchWeb] = useState(false); // Use boolean
  const [isSending, setIsSending] = useState(false); // Add loading state

  const genreSelected = selectedGenre !== null; // Derived state

  const handleGenreClick = useCallback((genreValue: string) => {
    setSelectedGenre(genreValue);
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || !selectedGenre || isSending) return;

    setSendPressed(true);
    setIsSending(true); // Set loading state

    const userMessage: Message = { text: input, sender: "user" };
    const currentMessages = [...messages, userMessage];
    setMessages(currentMessages);
    setInput(""); // Clear input immediately

    // Prepare history (last 5 messages excluding the latest user message)
    const historyMessages = messages
      .slice(-5) // Get last 5 messages from the previous state
      .map((msg) => `${msg.sender}: ${msg.text}`)
      .join("\n");

    try {
      const response = await performSearch(
        input,
        selectedGenre,
        historyMessages,
        model,
        model === DEFAULT_MODEL ? "API_KEY" : apiKey, // Use default key only for default model
        searchWeb
      );
      const botReply: Message = { text: response.summary, sender: "bot" };
      returnOptions(response.similar_docs);
      setMessages([...currentMessages, botReply]);
    } catch (error) {
      console.error("Error sending message:", error); // Log error
      const errorReply: Message = {
        text: "Error fetching response. Please try again!",
        sender: "bot",
      };
      setMessages([...currentMessages, errorReply]);
    } finally {
      setIsSending(false); // Reset loading state
    }
  }, [
    input,
    selectedGenre,
    isSending,
    messages,
    model,
    apiKey,
    searchWeb,
    returnOptions,
  ]);

  const handleModelChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const newModel = e.target.value;
      setModel(newModel);
      // Only show modal if a non-default model is selected and no API key is present
      if (newModel !== DEFAULT_MODEL && !apiKey) {
        setShowModal(true);
      } else if (newModel === DEFAULT_MODEL) {
        // If switching back to default, clear API key and hide modal
        setApiKey("");
        setShowModal(false);
      }
    },
    [apiKey]
  ); // Depend on apiKey

  const handleConfirmApiKey = useCallback(() => {
    if (apiKey.trim()) {
      // Ensure API key is not just whitespace
      setShowModal(false);
    }
  }, [apiKey]);

  const handleCancelApiKey = useCallback(() => {
    setModel(DEFAULT_MODEL); // Revert to default model
    setApiKey(""); // Clear API key
    setShowModal(false);
  }, []);

  const toggleSearchWeb = useCallback(() => {
    setSearchWeb((prev) => !prev);
  }, []);

  // Memoize message list rendering
  const messageList = useMemo(() => {
    const renderedMessages = messages.map((msg, index) => (
      <div key={index} className={`message ${msg.sender}`}>
        <ReactMarkdown>{msg.text}</ReactMarkdown>
      </div>
    ));
    if (isSending) {
      renderedMessages.push(
        <div key="typing" className="message bot typing-indicator">
          <span>.</span><span>.</span><span>.</span> {/* Simple dot animation */}
        </div>
      );
    }

    return renderedMessages;
  }, [messages, isSending]);

  return (
    <div className="chat-container">
      <div className="chat-box">
        {sendPressed ? (
          messageList
        ) : (
          <div className="chat-welcome">
            <div className="chat-greet">
              {/* Model Selector */}
              <div>
                <select
                  name="ModelSelect"
                  id="model"
                  value={model}
                  className="px-1"
                  onChange={handleModelChange}
                  aria-label="Select Model"
                >
                  {MODEL_OPTIONS.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>

                {/* API Key Modal */}
                {showModal && (
                  <div className="modal-overlay">
                    <div className="modal">
                      <div className="modal-header">
                        <h2>
                          Enter your API Key for{" "}
                          {MODEL_OPTIONS.find((m) => m.value === model)?.label}
                        </h2>
                      </div>
                      <div className="modal-body">
                        <input
                          type="password" // Use password type for API keys
                          className="input-field"
                          placeholder="Enter API Key"
                          value={apiKey}
                          onChange={(e) => setApiKey(e.target.value)}
                          aria-label="API Key Input"
                        />
                      </div>
                      <div className="modal-footer">
                        <button
                          className="btn cancel-btn"
                          onClick={handleCancelApiKey}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn confirm-btn"
                          onClick={handleConfirmApiKey}
                          disabled={!apiKey.trim()} // Disable if API key is empty or whitespace
                        >
                          Confirm
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <h1>How can I help you?</h1>
              <p>Please select the Document type</p>
            </div>
            {/* Genre Selector */}
            <div>
              {GENRE_OPTIONS.map((item) => (
                <button
                  className={`genre-opt ${
                    selectedGenre === item.value ? "active-btn" : ""
                  }`}
                  key={item.value} // Use value as key
                  onClick={() => handleGenreClick(item.value)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      {/* Input Area */}
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            genreSelected
              ? "What's on your mind?"
              : "Please select a genre first"
          }
          disabled={!genreSelected || isSending} // Disable if no genre or sending
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }} // Send on Enter key
          aria-label="Chat Input"
        />
        <button
          id="wiki-btn"
          className={`wiki-search ${searchWeb ? "search-web-active" : ""}`}
          onClick={toggleSearchWeb}
          title={searchWeb ? "Disable Web Search" : "Enable Web Search"}
          aria-pressed={searchWeb}
          disabled={isSending} // Disable during send
        >
          Search Web
        </button>
        <button
          id="send-btn"
          onClick={sendMessage}
          disabled={!input.trim() || !genreSelected || isSending} // More robust disable condition
        >
          {isSending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default Chat;
