import React from "react";
import Logo from "../images/logo.png"; 

export const Navbar = ({ title }) => {
  return (
    <nav className="flex items-center justify-between bg-cyan-800 h-20">
      <div className="w-full h-15 bg-cyan-50 mb-2 mt-2 flex items-center justify-between px-3 d-flex">
        <div className="flex items-center">
          <span className="font-san block mt-1 lg:inline-block lg:mt-0 font-bold text-cyan-800">
            {title}
          </span>
        </div>
        <div className="flex items-center">
          <img
            src={Logo}
            alt="Logo"
            className="h-50 w-270  ml-auto"
          />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;