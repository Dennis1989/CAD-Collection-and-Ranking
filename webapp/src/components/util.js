import React from "react";

// this is an enum that encodes all operations that we consider in the 'recursive' calls
export const StepInformation = {
  keep: 'keep',
  remove: 'remove',
  insert: 'insert',
  edit: 'edit',
  end: 'end'
}

// factory to generate an object that encodes the step information
// in a cell of our dynamic programming table
// theoretically, lastOperation can be reconstructed from distance
// but this yields a nicer algo
function createCellInfo(distance, lastOperation) {
  if (distance < 0) {
    throw new Error("Levenshtein distance can't be negative!")
  }
  if (Object.values(StepInformation).indexOf(lastOperation) === -1) {
    throw new Error("Unknown operation!" + lastOperation)
  }
  return {
    distance: distance,
    lastOperation: lastOperation
  }
}

export function levenshteinDistance(sentence1, sentence2) {
  const words1 = sentence1.split(" ")
  const words2 = sentence2.split(" ")

  const table = getLevenshteinTable(words1, words2)
  // return last element in 2d table
  return table[words2.length][words1.length].distance;
}

export function getLevenshteinOplist(words1, words2) {
  // get table
  const table = getLevenshteinTable(words1, words2)

  let i = words1.length
  let j = words2.length

  let high1 = []
  let high2 = []

  while (i > 0 || j > 0) {
    let entry = table[j][i]
    let op = entry.lastOperation
    switch(op) {
      case StepInformation.remove:
        i -= 1
        high1.unshift(op)
        break;
      case StepInformation.insert:
        j -= 1
        high2.unshift(op)
        break;
      case StepInformation.keep:
        j -= 1
        i -= 1
        high1.unshift(op)
        high2.unshift(op)
        break;
      case StepInformation.edit:
        j -= 1
        i -= 1
        high1.unshift(op)
        high2.unshift(op)
        break;
      default:
        throw new Error("Encountered invalid action <"+ op +"> during backtrack.")
    }
  }

  return [high1, high2]
}

function getLevenshteinTable(words1, words2) {
  // initialize our table
  const track = Array(words2.length + 1)
    .fill(null)
    .map(() => Array(words1.length + 1).fill(null));

  // now we consider the 'recursion base'
  track[0][0] = createCellInfo(0, StepInformation.end)
  for (let i = 1; i <= words1.length; i += 1) {
    // in these cases the first sentence is ε
    // => the optimal solution is to insert the i words of the 2nd sentence
    track[0][i] = createCellInfo(i, StepInformation.remove);
  }
  for (let j = 1; j <= words2.length; j += 1) {
    // in this case the second sentence is empty
    track[j][0] = createCellInfo(j, StepInformation.insert);
  }

  // now for the 'inductive' cases
  for (let j = 1; j <= words2.length; j += 1) {
    for (let i = 1; i <= words1.length; i += 1) {
      // determine the minimum
      const indicator = words1[i - 1] === words2[j - 1] ? 0 : 1;
      const best_dist = Math.min(
        track[j][i - 1].distance + 1, // deletion
        track[j - 1][i].distance + 1, // insertion
        track[j - 1][i - 1].distance + indicator, // substitution&keep
      );

      // recreate the last op
      // TODO: is this clean?
      var last_op = undefined
      switch(best_dist) {
        case track[j][i-1].distance + 1:
          last_op = StepInformation.remove
          break;
        case track[j-1][i].distance + 1:
          last_op = StepInformation.insert
          break;
        case track[j-1][i-1].distance:
          last_op = StepInformation.keep
          break;
        case track[j-1][i-1].distance + 1:
          last_op = StepInformation.edit
          break;
        default:
          throw new Error("Could not infer last action")
      }

      track[j][i] = createCellInfo(best_dist, last_op)
    }
  }

  return track
}



export function getInfrequentTokens(sentences) {
  const tokenCount = {};
  // this threshold
  const tokenThreshold = 0.7;

  // count token frequencies
  sentences.forEach((sentence) => {
    const tokens = sentence.split(/\s+/);
    tokens.forEach((token) => {
      // Convert the token to lowercase before counting
      const lowerCaseToken = token.toLowerCase();
      tokenCount[lowerCaseToken] = (tokenCount[lowerCaseToken] || 0) + 1;
    });
  });

  // normalize
  const numSentences = sentences.length;
  Object.keys(tokenCount).forEach((token) => {
    tokenCount[token] = tokenCount[token] / numSentences;
  });

  // filter out frequent tokens
  const infrequentTokens = Object.keys(tokenCount).filter(
    (token) => tokenCount[token] < tokenThreshold
  );

  console.log(infrequentTokens);
  return infrequentTokens;
}
