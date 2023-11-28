import React from "react";

export function SkipCadExplanationPopup({
  explanation,
  setExplanation,
  onBack,
  onSubmit,
}) {
  return (
    <div
      className="relative z-10"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* source: https://tailwindui.com/components/application-ui/overlays/modals */}

      {/* TODO: Animations not working right now */}

      {/*
        Background backdrop, show/hide based on modal state.

        Entering: "ease-out duration-300"
          From: "opacity-0"
          To: "opacity-100"
        Leaving: "ease-in duration-200"
          From: "opacity-100"
          To: "opacity-0"
      */}

      <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          {/*
            Modal panel, show/hide based on modal state.

            Entering: "ease-out duration-300"
              From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              To: "opacity-100 translate-y-0 sm:scale-100"
            Leaving: "ease-in duration-200"
              From: "opacity-100 translate-y-0 sm:scale-100"
              To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    */}

          <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
            <div className="bg-white px-4 pt-5">
              <div className="text-center sm:ml-4 sm:mt-0 sm:text-left">

                {/* Message */}

                <h3
                  className="text-base font-semibold leading-6 text-gray-900"
                  id="modal-title"
                >
                  Don't think this sentence is sexist?
                </h3>
                <div className="mt-2 mb-2">
                  <p className="text-sm text-gray-500">
                    Please provide an explanation why you don't think this
                    sentence is sexist.
                  </p>
                </div>

                {/* Explanation input */}
                <div className="flex justify-center w-full">
                  <div className="w-full">
                    <input
                      className="w-full shadow appearance-none border rounded w-1/2 mb-3 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="explanation-input"
                      type="text"
                      placeholder=""
                      onChange={(e) => setExplanation(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                type="button"
                className="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                onClick={(e) => onSubmit()}
              >
                Submit
              </button>
              <button
                type="button"
                className="inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                onClick={(e) => onBack()}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
