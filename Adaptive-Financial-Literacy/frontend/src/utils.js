export function prettyTopic(topic) {
  return topic.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatINR(n, decimals = 2) {
  return "₹" + Number(n).toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}