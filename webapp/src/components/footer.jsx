import React, { useState, useEffect } from "react";
import Modal from "./Datapopup.jsx";
import DataPolicy from "./DataAndPolicy.jsx";
import { FeedbackPopup } from "./FeedbackPopup.jsx";

function Footer({ submitFeedback }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const [feedback, setFeedback] = useState("");
  const [showFeebackPopup, setShowFeebackPopup] = useState(false);

  function onFeedbackBack() {
    setShowFeebackPopup(false);
  }
  function onFeedbackShow() {
    setShowFeebackPopup(true);
  }
  function onFeedbackSubmit() {
    setShowFeebackPopup(false);
    submitFeedback(feedback);
    setFeedback("");
  }

  return (
    <div className="flex flex-col ">
      <footer className="text-black flex justify-center  text-center cursor-pointer text-cyan-500">
          <button className="hover:underline px-4 py-2" onClick={openModal}>
            Data and Policy
          </button>
          {isModalOpen && (
            <Modal content={<DataPolicy />} onClose={closeModal} />
          )}

        {(submitFeedback !== undefined) &&
        (
          <>
            <button
              className="bg-cyan-800 hover:bg-cyan-500 flex text-white font-bold py-2 px-4 rounded-full"
              onClick={onFeedbackShow}
            >
              Feedback
            </button>
            <FeedbackPopup
              feedback={feedback}
              setFeedback={setFeedback}
              onSubmit={onFeedbackSubmit}
              onBack={onFeedbackBack}
              showProp={showFeebackPopup}
            />
          </>
        )}
      </footer>
    </div>
  );
}

export default Footer;
