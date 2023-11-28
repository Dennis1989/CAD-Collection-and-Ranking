import React from "react";
function LCSFinder({ sentences }) {
    const findLCS = (str1, str2) => {
      const m = str1.length;
      const n = str2.length;
      const dp = [];
  

      for (let i = 0; i <= m; i++) {
        dp[i] = new Array(n + 1).fill(0);
      }
  
  
      for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
          if (str1[i - 1] === str2[j - 1]) {
            dp[i][j] = dp[i - 1][j - 1] + 1;
          } else {
            dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
          }
        }
      }
  
   
      let i = m;
      let j = n;
      const lcs = [];
      while (i > 0 && j > 0) {
        if (str1[i - 1] === str2[j - 1]) {
          lcs.unshift(str1[i - 1]);
          i--;
          j--;
        } else if (dp[i - 1][j] > dp[i][j - 1]) {
          i--;
        } else {
          j--;
        }
      }
  
      const lcsStr = lcs.join('');
  
      return lcsStr;
    };
  
    const highlightNonLCS = (sentence, lcs) => {
      const words = sentence.split(' ');
      const highlightedWords = [];
  
      for (const word of words) {
        if (lcs.includes(word)) {
          highlightedWords.push(word);
        } else {
          highlightedWords.push(
            <span key={word} style={{ color: 'blue' }}>
              {word}
            </span>
          );
        }
        highlightedWords.push(' '); 
      }
  
      return highlightedWords;
    };

  
  
    let lcs = sentences[0];
    for (let i = 1; i < sentences.length; i++) {
      lcs = findLCS(lcs, sentences[i]);
    }
  
    return (
      <div>
 
        <div>
          {sentences.map((sentence, index) => (
            <p key={index}>{highlightNonLCS(sentence, lcs)}</p>
          ))}
        </div>
      </div>
    );
  }
  
  export default LCSFinder;
  