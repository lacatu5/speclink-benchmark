export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatPriority(priority) {
  const labels = { 1: "Low", 2: "Medium", 3: "High" };
  return labels[priority] || "Unknown";
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}
