export default function MissingEvidence({ items }: { items: string[] }) {
  if (!items.length) return <div className="quiet-note">No missing evidence was reported for this criterion.</div>
  return <ul className="missing-list">{items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}</ul>
}
