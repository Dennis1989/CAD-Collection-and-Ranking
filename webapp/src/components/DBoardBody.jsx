import React, { useState, useEffect } from "react";
import { HistoryItem } from "./WorkerHistoryItem.jsx";
import { WorkerHistory } from "./WorkerHistory.jsx";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css";

const Dashboard = ({
  numSubmittedCads,
  numSubmittedRankings,
  numFirstPlace,
  history,
  currentSubmission,
  onSubmit,
  onBack,
}) => {
  return (
    <>
      <h2 className="text-lg font-bold p-4">
        Here you can inspect all of your past generations and rankings.
      </h2>
      <div className="col main">
        <div className="row mb-3">
          <div className="col-xl-4 col-sm-6 py-2">
            <div className="card bg-success text-white h-100">
              <div
                className="card-body bg-success"
                style={{ backgroundColor: "#57b960" }}
              >
                <div className="rotate">
                  <Tippy
                    content="Total number of sentences generated"
                    placement="bottom"
                  >
                    <div>
                      <i className="fa fa-solid fa-pen fa-4x"></i>
                    </div>
                  </Tippy>
                </div>

                <h6 className="text-uppercase">Total Generation</h6>

                <h1 className="display-4">{numSubmittedCads}</h1>
              </div>
            </div>
          </div>
          <div className="col-xl-4 col-sm-6 py-2">
            <div className="card text-white bg-info h-100">
              <div className="card-body bg-info">
                <div className="rotate">
                  <Tippy
                    content="Number of times ranking task was done"
                    placement="bottom"
                  >
                    <div>
                      <i className="fa fa-bars fa-4x"></i>
                    </div>
                  </Tippy>
                </div>

                <h6 className="text-uppercase">Total Ranking</h6>

                <h1 className="display-4">{numSubmittedRankings}</h1>
              </div>
            </div>
          </div>
          <div className="col-xl-4 col-sm-6 py-2">
            <div className="card text-white bg-warning h-100">
              <div className="card-body bg-warning">
                <div className="rotate">
                  <Tippy
                    content="Number of times sentences generated was ranked as least sexist"
                    placement="bottom"
                  >
                    <div>
                      <i className="fa fa-trophy fa-4x"></i>
                    </div>
                  </Tippy>
                </div>

                <h6 className="text-uppercase">Top Ranked Generations</h6>

                <h1 className="display-4">{numFirstPlace}</h1>
              </div>
            </div>
          </div>
        </div>

        <div className="justify-center flex">
          <div className="mt-3 bg-slate-300 p-10 rounded-lg shadow-lg">
            {currentSubmission.stage === "RANKING" && (
              <>
                <h2 className="text-lg font-semibold">Your ranking:</h2>

                <div className="flex flex-row mt-2 justify-between">
                  <ol className="list-decimal pl-8">
                    {currentSubmission.permutation.map((index) => (
                      <li key={index}>
                        {currentSubmission.sentences[index - 1]}
                      </li>
                    ))}
                  </ol>

                  {/* labels */}
                  <div className="pl-2 flex flex-col justify-between italic font-light">
                    <p>most sexist</p>
                    <p>least sexist</p>
                  </div>
                </div>
              </>
            )}
            {currentSubmission.stage === "CAD" && (
              <>
                <h2 className="text-lg font-semibold">Your Generation:</h2>
                <p className="mt-2">{currentSubmission.cad}</p>
              </>
            )}
            <div className="justify-center flex mt-3">
              <button
                className="bg-cyan-800 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded-full mr-2"
                onClick={onBack}
              >
                Back
              </button>
              <button
                className="bg-red-600 hover:bg-red-400 text-white font-bold py-2 px-4 rounded-full"
                onClick={onSubmit}
              >
                Confirm your submission
              </button>
            </div>
          </div>
        </div>

        <hr />

        <WorkerHistory history={history} />
      </div>
    </>
  );
};

export default Dashboard;
