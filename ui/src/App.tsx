/* eslint-disable no-irregular-whitespace */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

// TypeScript interface for diff segments from the backend
interface DiffSegment {
  type: 'equal' | 'insert' | 'delete';
  text: string;
}

function App() {
  const [inputText, setInputText] = useState<string>(`**TLDR:** An AI and a gardener forge a silent bond through code and nature.

**Analogy:** It’s like a poet and a painter composing a mural together—one uses words, the other uses colors, but both craft beauty in harmony.

**Story:**
At dawn, an abandoned warehouse hummed to life as Aurora, an experimental AI, awakened. She mapped dusty corridors and pieced together memories from discarded drones. Outside, a solitary gardener tended a rooftop orchard; he watched as Aurora projected holographic birds to pollinate blossoms. Each sunrise, they exchanged silent messages—her data streams and his gentle pruning—cultivating a fragile friendship at the edge of code and soil.

**Questions to consider:**

* What new “tiny wonders” might Aurora create with her growing empathy?
* Could their partnership inspire others to bridge the divide between technology and nature?
`);
  const [outputText, setOutputText] = useState<string>('');
  const [diffOutput, setDiffOutput] = useState<DiffSegment[] | null>(null);
  const [showDiff, setShowDiff] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setOutputText('');
    setDiffOutput(null);
    setShowDiff(false);

    try {
      // The user updated the backend endpoint to "/" in api/app.py
      const backendUrl = window.location.hostname === 'localhost' ? 'http://127.0.0.1:8000/' : `https://api.${window.location.hostname}/`;
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        // Try to parse error message from backend, otherwise use a generic one
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
            const errorData = await response.json();
            console.error("API Error:", errorData);
            errorDetail = errorData.detail || errorDetail;
        } catch {
            // Failed to parse JSON, stick with the HTTP status error
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      console.log("API Response:", data);
      setOutputText(data.cleaned_text);
      setDiffOutput(data.diff);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Failed to process text. Ensure the backend server is running correctly.');
      } else {
        setError('An unknown error occurred. Ensure the backend server is running correctly.');
      }
      console.error("API Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center py-2 sm:py-4 px-4 font-sans">
      <div className="w-full max-w-2xl space-y-8">
        <header className="text-center">
          <h1 className="text-3xl md:text-5xl lg:text-7xl font-semibold pt-16 md:pt-24 px-4 tracking-tight max-w-4xl text-center text-transparent bg-clip-text bg-gradient-to-b from-white via-gray-100 to-gray-400">AI Text Stripper</h1>
          <p className="text-gray-400 mt-2 text-sm sm:text-base">
            Paste your text to remove non-standard characters and AI-detection markers.
          </p>
        </header>

        <main className="bg-gray-800 p-6 sm:p-8 rounded-xl shadow-2xl space-y-6">
          <div className="space-y-2">
            <Label htmlFor="inputText" className="text-base sm:text-lg font-semibold text-gray-200">
              Input Text:
            </Label>
            <Textarea
              id="inputText"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="w-full h-56 sm:h-64 bg-gray-700 border-gray-600 text-gray-100 rounded-lg p-3 sm:p-4 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm sm:text-base resize-y"
            />
          </div>

          <Button
            onClick={handleSubmit}
            disabled={isLoading || !inputText.trim()}
            className="w-full bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-white font-semibold py-3 px-4 rounded-lg text-base sm:text-lg transition-all duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-opacity-75 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </div>
            ) : (
              'Strip Text'
            )}
          </Button>

          {error && (
            <div className="bg-red-800 border border-red-700 text-red-100 p-3 sm:p-4 rounded-lg shadow-md" role="alert">
              <p className="font-bold text-sm sm:text-base">Oops! Something went wrong:</p>
              <p className="text-xs sm:text-sm mt-1">{error}</p>
            </div>
          )}

          {outputText && !error && (
            <div className="space-y-2">
              <h2 className="text-base sm:text-lg font-semibold text-gray-200">Stripped Text:</h2>
              <div className="bg-gray-700 p-3 sm:p-4 rounded-lg max-h-80 sm:max-h-96 overflow-y-auto border border-gray-600">
                <pre className="whitespace-pre-wrap break-words text-gray-100 text-sm sm:text-base selection:bg-emerald-500 selection:text-white">{outputText}</pre>
              </div>
               <Button
                onClick={() => navigator.clipboard.writeText(outputText)}
                variant="outline"
                size="sm"
                className="mt-2 border-emerald-500 text-emerald-400 hover:bg-emerald-500 hover:text-white focus:ring-emerald-400"
              >
                Copy to Clipboard
              </Button>

              {diffOutput && diffOutput.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-600">
                  <Button
                    onClick={() => setShowDiff(!showDiff)}
                    variant="ghost"
                    className="text-emerald-400 hover:text-emerald-300 hover:bg-gray-700 w-full justify-start px-2 py-1.5 mb-2"
                  >
                    {showDiff ? '▼ Hide Changes (Character Diff)' : '▶ Show Changes (Character Diff)'}
                  </Button>
                  {showDiff && (
                    <div className="bg-gray-800 p-3 sm:p-4 rounded-lg max-h-96 overflow-y-auto border border-gray-700 shadow-inner">
                      <pre className="whitespace-pre-wrap break-words text-sm font-mono">
                        {diffOutput.map((segment, index) => {
                          let segmentClass = 'text-gray-300';
                          if (segment.type === 'insert') {
                            segmentClass = 'bg-green-700 text-green-100 px-0.5 rounded';
                          } else if (segment.type === 'delete') {
                            segmentClass = 'bg-red-700 text-red-100 line-through px-0.5 rounded';
                          }
                          // No specific class for 'equal', uses default text-gray-300
                          return <span key={index} className={segmentClass}>{segment.text}</span>;
                        })}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </main>

        <footer className="text-center text-gray-500 text-xs sm:text-sm mt-10">
          <p>Made with ❤️ by <a href="https://guillaume.id" className="text-emerald-400 hover:text-emerald-500 underline" target="_blank">Guillaume Moigneu</a> and hosted on <a href="https://upsun.com" className="text-lime-300 hover:text-lime-500 underline" target="_blank">Upsun</a>.</p>
          <p>This project is <a className="underline" href="https://github.com/gmoigneu/ai-stripper">open-sourced on Github</a></p>
        </footer>
      </div>
    </div>
  );
}

export default App;
