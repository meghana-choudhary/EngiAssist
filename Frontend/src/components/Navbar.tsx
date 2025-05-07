import React from "react";
import { Link } from "react-router-dom";
import "../css/navbar.css";
// import logo from "../assets/engi.jpg"

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1 className="logo">
          <span className="logo-text">Engi</span>
          <span className="logo-highlight">Assist</span>
        </h1>
      </div>
      <div className="navbar-links">
        <Link to="/" className="nav-link">Home</Link>
        <Link target="_blank" to="https://github.com/meghana-choudhary/EngiAssist" className="nav-link">GitHub</Link>
      </div>
    </nav>
  );
};

export default Navbar;