import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Evaluation from './pages/Evaluation'
import JudgeComparison from './pages/JudgeComparison'

function NotFound() { return <main className="page-shell empty-state"><span className="eyebrow">404 · PAGE NOT FOUND</span><h1>This page isn’t in the rubric.</h1><a className="button button-primary" href="/">Return home</a></main> }

export default function App() {
  return <BrowserRouter><Navbar/><Routes><Route path="/" element={<Home/>}/><Route path="/evaluation" element={<Evaluation/>}/><Route path="/judges" element={<JudgeComparison/>}/><Route path="*" element={<NotFound/>}/></Routes><footer className="footer"><div><span className="brand-mark footer-mark">F</span><strong>FairJudge AI</strong><span>Evidence supports decisions. Humans make them.</span></div><span>Local AI · Open tools · Human authority</span></footer></BrowserRouter>
}
