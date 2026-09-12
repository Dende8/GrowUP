export default function InsightCard({ number, title, children }) {
  return (
    <article className="insight-card">
      <div className="card-number">{number}</div>
      <h3>{title}</h3>
      <p>{children}</p>
      <span className="card-arrow" aria-hidden="true">↗</span>
    </article>
  );
}
