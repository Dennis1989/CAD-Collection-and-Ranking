import React, { useState } from "react";
// alert taken from here: https://v1.tailwindcss.com/components/alerts
// icon taken from here: https://tailwindui.com/components/application-ui/overlays/modals

export function ContentWarning() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div role="alert" className="text-left">
      <div className="bg-red-500 text-white font-bold rounded-t-2xl px-4 py-2 flex">
        <svg
          class="h-6 w-6 text-red-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="white"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
          />
        </svg>
        <div className="ml-2">Content Warning</div>
      </div>
      <div className="border border-t-0 border-red-400 rounded-b-2xl bg-red-100 px-4 py-3 text-red-700">
        <p>
          The content was taken from the uncensored internet. You may find some
          of the content upsetting. Unfortunately, we can't give you an
          exhaustive and specific description of the type of content you will
          encounter.
        </p>
        {!expanded && (
          <>
            {" "}
            <span
              onClick={(e) => setExpanded(true)}
              className="text-blue-500 underline"
            >
              more
            </span>
          </>
        )}

        {expanded && (
          <>
            <p>
              However, we expect that this task contains{" "}
              <span className="font-bold">
                sexism, ableism, racism, classism, discrimination based on
                sexual identity, fat phobia, violence
              </span>{" "}
              and in other ways explicit content.
            </p>

            <p>
              While it's crucial for us to study them, we do not endorse any of
              the statements.
            </p>

            <p>
              If you have concerns, questions, or strong negative reactions to
              some of the content, please either{" "}
              <a
                href="mailto:Dennis.Assenmacher@gesis.org"
                className="text-blue-500"
              >
                email us
              </a>
              , use the feedback function inside the task or{" "}
              <a
                href="https://www.crisistextline.org"
                className="text-blue-500"
              >
                reach out
              </a>{" "}
              if in crisis.
            </p>
            <>
              <span
                onClick={(e) => setExpanded(false)}
                className="text-blue-500 underline"
              >
                less
              </span>
            </>
          </>
        )}
      </div>
    </div>
  );
}
