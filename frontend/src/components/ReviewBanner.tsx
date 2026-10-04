export default function ReviewBanner({ detail = 'Review the evidence and rubric interpretation before making a final decision.' }: { detail?: string }) {
  return <section className="review-banner" role="status"><span className="review-icon" aria-hidden="true">!</span><div><strong>Human review recommended</strong><p>FairJudge detected information that needs a judge’s attention. {detail}</p></div></section>
}
