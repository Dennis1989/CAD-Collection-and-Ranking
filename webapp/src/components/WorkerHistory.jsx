import React, { useEffect, useState } from "react";
import { WorkerHistoryItem } from "./WorkerHistoryItem.jsx";

export function WorkerHistory({ history }) {
  const entries_per_page = 6;
  const [page, setPage] = useState(0);

  const [startEntry, setStartEntry] = useState(0);
  const [endEntry, setEndEntry] = useState(Math.min(entries_per_page, history.length));
  const [currentEntries, setCurrentEntries] = useState(history.slice(startEntry, endEntry));

  function onNextPage() {
    if (page < Math.ceil(history.length / entries_per_page) - 1) {
      let new_page = page+1
      let start = new_page * entries_per_page
      let end = Math.min(entries_per_page * (new_page + 1), history.length)
      setPage(new_page)
      setStartEntry(start)
      setEndEntry(end)
      setCurrentEntries(history.slice(start, end))
    }
  }

  function onPrevPage() {
    if (page > 0) {
      let new_page = page-1
      let start = new_page * entries_per_page
      let end = Math.min(entries_per_page * (new_page + 1), history.length)
      setPage(new_page)
      setStartEntry(start)
      setEndEntry(end)
      setCurrentEntries(history.slice(start, end))
    }
  }

  return (
    <div className="row ">
      <div className="col-lg-12 col-md-15 col-sm-20">
        <h5 className="mt-3 mb-3 text-xl text-black pl-2">Past submissions</h5>
        <div className="table-responsive">
          <table className="table">
            <colgroup>
              <col span="1" className="w-[5%]"></col>
              <col span="1" className="w-[40%]"></col>
              <col span="1" className="w-[40%]"></col>
              <col span="1" className="w-[15%]"></col>
            </colgroup>

            <thead className="thead-light">
              <tr>
                <th></th>
                <th>Type</th>
                <th>Time Completed</th>
                <th>Details</th>
              </tr>
            </thead>

            <tbody>
              {currentEntries.map((entry) => (
                <WorkerHistoryItem item={entry} />
              ))}
            </tbody>
          </table>
          <div class="flex flex-col items-center mb-4">
            <span class="text-sm text-gray-700 ">
              Showing{" "}
              <span class="font-semibold text-gray-900">
                {history.length > 0 && (startEntry + 1)}
                {history.length === 0 && (0)}
                </span>{" "}
              to{" "}
              <span class="font-semibold text-gray-900">
                {endEntry}
              </span>{" "}
              of{" "}
              <span class="font-semibold text-gray-900">
                {history.length}
              </span>{" "}
              Entries
            </span>
            <div class="inline-flex mt-2 xs:mt-0">
              <button class="flex items-center justify-center px-3 h-8 text-sm font-medium text-white bg-gray-800 rounded-l hover:bg-gray-900"
                onClick={onPrevPage}
                disabled={page == 0}
              >
                Prev
              </button>
              <button class="flex items-center justify-center px-3 h-8 text-sm font-medium text-white bg-gray-800 border-0 border-l border-gray-700 rounded-r hover:bg-gray-900"
                onClick={onNextPage}
                disabled={endEntry===history.length}
                >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
