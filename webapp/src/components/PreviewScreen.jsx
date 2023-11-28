import React, { useState } from "react";
import { levenshteinDistance, getInfrequentTokens } from "./util.js";
import { TextComparison } from "./TextComparison.jsx";
import { ContentWarning } from "./ContentWarning.jsx";
import Footer from "./footer.jsx";

export function PreviewScreen() {
  const [isContentVisible, setIsContentVisible] = useState(false);

  const toggleContentVisibility = () => {
    setIsContentVisible(!isContentVisible);
  };

  // Define exampleranking here, outside of the toggleContentVisibility function
  const exampleranking = [
    "Women are less intelligent than men.",
    "Flies are less intelligent than dogs.",
    "Women are less tall.",
    "Women are as intelligent as men.",
  ];

  const infrequentTokens = getInfrequentTokens(exampleranking);

  const colorToken = (token) => {
    const lowerCaseToken = token.toLowerCase(); // Convert token to lowercase
    if (infrequentTokens.includes(lowerCaseToken)) {
      // Color infrequent tokens
      return <span className="font-extrabold">{token}</span>;
    } else {
      // Regular tokens
      return token;
    }
  };

  return (
    <div className="flex justify-center w-full">
      <div className="p-10 w-full md:w-[80%] flex flex-col gap-4">
        <div className="p-2 bg-cyan-50 border border-gray-300 rounded-2xl font-medium text-gray-600">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-black mb-4 mt-2">
              Welcome to the Unsexify Game!
            </h1>

            <h2 className="text-base text-neutral-600">
              You will test your skills on two challenges:
            </h2>

            <div className="flex-row flex basis-full items-stretch justify-center">
              <div className="flex-initial w-100 block rounded-lg border-cyan-800 border-4 shadow-lg p-2 m-4">
                <h2 className="text-xl font-bold text-black">
                  Unsexify Modification
                </h2>
                Compete to remove sexism from a sentence, changing it as little
                as possible; the least sexist entry will earn a bonus.
                <br />
                <br />
                <p></p>
                <h3 className="text-xl font-bold text-black">
                  A modification you might make:
                </h3>
                <div className="flex items-center justify-center text-center">
                  <TextComparison
                    sentence1="Women are less intelligent than men."
                    sentence2="Women are as intelligent as men."
                  />
                </div>
                <div className="flex items-center justify-center text-center">
                  <TextComparison
                    sentence1="Women are less intelligent than men."
                    sentence2="Women are less tall."
                  />
                </div>
                <div className="flex items-center justify-center text-center">
                  <TextComparison
                    sentence1="Women are less intelligent than men."
                    sentence2="Flies are less intelligent than dogs."
                  />
                </div>
              </div>

              <div className="flex-initial w-100 block rounded-lg border-cyan-800 border-4 shadow-lg p-2 m-4">
                <h2 className="text-xl font-bold text-black">
                  Unsexify Ranking
                </h2>
                Rank variants of a sentence from least to most sexist; the
                ranking that is closest to those of other participants will earn
                a bonus.
                <br />
                <br />
                <h3 className="text-xl font-bold text-black">
                  {" "}
                  A ranking you might generate:
                </h3>
                <div className="flex justify-center mt-2 text-left">
                  <div className="flex flex-row">
                    <ol className="list-decimal pl-8">
                      {exampleranking.map((sentence, index) => (
                        <li key={index}>
                          {
                            /* Split sentence into tokens, apply coloring, and join them back */
                            sentence.split(/\s+/).map((token, i) => (
                              <React.Fragment key={i}>
                                {colorToken(token)}
                                {i < sentence.split(/\s+/).length - 1
                                  ? " "
                                  : ""}
                              </React.Fragment>
                            ))
                          }
                        </li>
                      ))}
                    </ol>

                    {/* labels */}
                    <div className="pl-2 flex flex-col justify-between italic font-light">
                      <p className="font-thin">most sexist</p>
                      <p className="font-thin">least sexist</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <p className="mb-4">
              If this sounds interesting to you{" "}
              <span className="font-extrabold">accept below</span>!
              </p>
              <p className="mb-4 italic">
              It is not advisable to use a mobile device for this task, as some of the features or options may be limited or restricted.
            </p>
          </div>
        </div>
        <ContentWarning />
        <div role="alert" className="text-left">
          <div className="bg-cyan-800 text-white font-bold rounded-t-2xl px-4 py-2 flex">
            <div className="ml-2">Research Background</div>
          </div>
          <div className="p-4 bg-cyan-50 rounded-b-2xl">
            <p>
              Our research team is dedicated to delving into the core mechanics
              of sexism and examining how computational models can efficiently
              utilize the nuances that differentiate between sexist and
              non-sexist sentences, with a particular focus on the use of
              counterfactuals.{" "}
            </p>
            <p>
              {" "}
              These counterfactuals are sentences that require minimal lexical
              changes to transform a sexist statement into a non-sexist one or
              vice versa.
            </p>
            <p>
              Our main goal is to enhance our comprehension of the subjective
              quality aspects associated with counterfactuals as perceived by
              individuals.
            </p>
          </div>
        </div>
        <Footer />
      </div>
    </div>
  );
}
