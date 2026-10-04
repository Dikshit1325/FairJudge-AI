export default function EvidenceList({ items, empty = 'No evidence was returned.' }: { items: string[]; empty?: string }) {
  return items.length ? <ul className="evidence-list">{items.map((item, index) => <li key={`${item}-${index}`}><span aria-hidden="true">↳</span>{item}</li>)}</ul> : <p className="muted small">{empty}</p>
}
