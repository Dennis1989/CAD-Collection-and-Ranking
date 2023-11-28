import React from "react";

function Modal({ content, onClose }) {
  return (
    <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-4/5 max-w-screen-xl">
        <div className="text-right">
          <button
            onClick={onClose}
            className="text-cyan-500 border-cyan-500"
          >
            Close
          </button>
        </div>
        <div className="overflow-y-auto h-96">
          {content}
        </div>
      </div>
    </div>
  );
}

export default Modal;