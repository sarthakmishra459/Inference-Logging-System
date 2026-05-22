export const formatPreview = (text: string | null | undefined) => {
    if (!text) return "No messages yet";
    // Replace all line breaks/newlines with a single space character
    const singleLine = text.replace(/\s+/g, " ");
    return singleLine.length > 35 ? `${singleLine.substring(0, 35)}...` : singleLine;
  };