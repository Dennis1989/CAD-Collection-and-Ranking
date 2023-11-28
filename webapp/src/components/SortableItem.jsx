import React from "react";
import Card from 'react-bootstrap/Card';
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

export function SortableItem(props) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition
  } = useSortable({ id: props.id, threshold: 40 }); // Increase the drag tolerance

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    marginBottom: "1rem",
    fontSize: "16px", // Reduce the font size
    padding: "0.5rem" // Reduce the padding
  };

  const wordsInSentence = props.sentence.split(/\s+/);

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}

      className="hover-card md:touch-action-none sm:touch-action-none"

    >
      <Card body>
        <div className='text-black'>
          {wordsInSentence.map((word, wordIndex) => {
            const isInfrequent = props.infrequentTokens.includes(word);
            return (
              <React.Fragment key={wordIndex}>
                {wordIndex > 0 ? ' ' : ''}
                {isInfrequent ? (
                  <span className="font-bold">{word}</span>
                ) : (
                  <span className="font-light">{word}</span>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
