import React from "react";
import { Link } from "react-router-dom";
import "../css/navbar.css";
import logo from "../assets/somnetics.svg"

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <img src={logo} alt="Brand Logo" className="logo"/>
      </div>
      <div className="navbar-links">
        <Link to="/" className="nav-link">Home</Link>
        <Link target="_blank" to="https://somneticstech.com/" className="nav-link">About Us</Link>
      </div>
    </nav>
  );
};

export default Navbar;
