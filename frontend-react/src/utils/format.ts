export function formatNumber(value: number | string): string {
  const numeric = Number(String(value).replace(/,/g, ""));
  if (!Number.isFinite(numeric)) return String(value);
  if (numeric >= 1000) {
    return `${(numeric / 1000).toFixed(numeric >= 10000 ? 1 : 0)}K`;
  }
  return String(numeric);
}

export function initials(title: string): string {
  return String(title || "AI")
    .split(/[\s/:-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}
