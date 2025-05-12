import axios, { AxiosError } from "axios";

// Define an interface for the expected API response structure
interface ChatApiResponse {
  summary: string;
  similar_docs: any[]; // Replace 'any' with a more specific type if known
  // Add other potential fields from the response if necessary
}

// Define an interface for the request payload
interface ChatApiPayload {
  query: string;
  queries: string;
  history: string;
  search_web: boolean;
}

// Read the API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.error(
    "Error: VITE_API_BASE_URL is not defined in the environment variables."
  );
  // You might want to throw an error or provide a default fallback,
  // but logging an error is often sufficient during development.
}

/**
 * Performs a search request to the chat API.
 * @param query - The user's search query.
 * @param queries- Past queries
 * @param history - The recent chat history.
 * @param search_web - Flag indicating whether to search the web.
 * @returns A promise that resolves with the API response.
 * @throws An error if the API request fails.
 */
export async function performSearch(
  query: string,
  queries: string,
  history: string,
  search_web: boolean
): Promise<ChatApiResponse> {
  const payload: ChatApiPayload = {
    query,
    queries,
    history,
    search_web,
  };

  try {
    const response = await axios.post<ChatApiResponse>(
      `${API_BASE_URL}/chat/`,
      payload
    );
    console.log("API Response:", response.data);
    return response.data;
  } catch (error) {
    // Log more specific error details if available
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      console.error("Error fetching chatbot response:", axiosError.message);
      if (axiosError.response) {
        console.error("Status:", axiosError.response.status);
        console.error("Data:", axiosError.response.data);
      }
    } else {
      console.error("An unexpected error occurred:", error);
    }
    // Re-throw the error to be handled by the calling component
    throw error;
  }
}
