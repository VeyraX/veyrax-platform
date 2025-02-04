"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AIInputWithSearch } from "../../agent/components/input/ai-input";

export default function GenerateMain() {
  const router = useRouter();
  const [isGenerating, setIsGenerating] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);
  
  const generationSteps = [
    "Reading API documentation...",
    "Generating model...",
    "Generating components...",
    "Generating routes..."
  ];

  useEffect(() => {
    if (isGenerating) {
      const stepDuration = 7500; // 7.5 seconds per step
      
      const intervalId = setInterval(() => {
        setGenerationStep(prev => {
          if (prev < generationSteps.length - 1) {
            return prev + 1;
          }
          clearInterval(intervalId);
          setIsGenerating(false);
          setShowSuccess(true);
          return prev;
        });
      }, stepDuration);

      return () => clearInterval(intervalId);
    }
  }, [isGenerating]);

  const handleSubmit = async (value: string) => {
    setIsGenerating(true);
    setGenerationStep(0);
  };

  const handleSuccessClick = () => {
    router.push('/generate/eventbright');
  };

  const handleFileSelect = (file: File) => {
    // Handle file selection logic here
    console.log(file);
  };

  const handleVoiceText = (text: string) => {
    // Handle voice text logic here
    console.log(text);
  };

  if (isGenerating || showSuccess) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center max-w-md w-full">
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold mb-4">{generationSteps[generationStep]}</h2>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((generationStep + 1) / generationSteps.length) * 100}%` }}
                ></div>
              </div>
            </>
          ) : (
            <>
              <h2 className="text-2xl font-bold mb-4">Success! 🎉</h2>
              <p className="mb-6">Your components are ready</p>
              <button
                onClick={handleSuccessClick}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                View Components
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <div className="flex flex-col items-center w-full max-w-2xl space-y-8">
        <h1 className="text-4xl font-bold text-center tracking-tight">Generate Composable Agent Components</h1>
        {!isGenerating ? (
          <div className="w-full">
            <AIInputWithSearch
              placeholder="Add link to API and ask AI to generate components..."
              onSubmit={handleSubmit}
              onFileSelect={handleFileSelect}
              onVoiceText={handleVoiceText}
            />
          </div>
        ) : (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-lg">Generating your components...</p>
          </div>
        )}
      </div>
    </div>
  );
}
