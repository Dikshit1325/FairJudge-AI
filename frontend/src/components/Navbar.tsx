import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return <header className="navbar"><div className="nav-inner"><NavLink to="/" className="brand" aria-label="FairJudge AI home"><span className="brand-mark">F</span><span>fairjudge<span className="brand-ai">.ai</span></span></NavLink><nav aria-label="Main navigation"><NavLink to="/evaluation">Evaluation</NavLink><NavLink to="/judges">Judge comparison</NavLink><a href="/#about">About</a></nav><div className="nav-status"><span className="status-dot"/>Local model</div></div></header>
}
