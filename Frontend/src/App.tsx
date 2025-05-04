import Navbar from "./components/Navbar";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./css/style.css";
import { Hero } from "./components/Hero";
// import PdfViewerPage from './components/PdfViewerPage';
// import "bootstrap/dist/css/bootstrap.min.css"
import PdfViewerPage from "./components/PdfViewerPage";

const App = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/pdf/:filename/:page" element={<PdfViewerPage />} />
      </Routes>
    </Router>
  );
};

export default App;
