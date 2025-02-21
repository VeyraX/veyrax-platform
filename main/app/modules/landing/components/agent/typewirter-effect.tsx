import { useEffect, useState } from "react";

interface TypewriterEffectProps {
  texts: string[];
  typingSpeed?: number;
  deletingSpeed?: number;
  pauseTime?: number;
}

export const TypewriterEffect = ({
  texts,
  typingSpeed = 100,
  deletingSpeed = 50,
  pauseTime = 1500,
}: TypewriterEffectProps) => {
  const [typewriterIndex, setTypewriterIndex] = useState(0);
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const typewriter = () => {
      const currentText = texts[typewriterIndex];
      
      if (!isDeleting) {
        if (displayText === currentText) {
          setTimeout(() => setIsDeleting(true), pauseTime);
          return;
        }
        setDisplayText(currentText.substring(0, displayText.length + 1));
      } else {
        if (displayText === "") {
          setIsDeleting(false);
          setTypewriterIndex((prev) => (prev + 1) % texts.length);
          return;
        }
        setDisplayText(currentText.substring(0, displayText.length - 1));
      }
    };

    const timer = setTimeout(
      typewriter,
      isDeleting ? deletingSpeed : typingSpeed
    );

    return () => clearTimeout(timer);
  }, [displayText, isDeleting, typewriterIndex, texts, typingSpeed, deletingSpeed, pauseTime]);

  return <span className="text-spektr-cyan-50">/ {displayText}</span>;
};