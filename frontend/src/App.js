import React, { useState, useCallback, useEffect } from "react";
import "@/App.css";
import { Upload, Home, Loader2, CheckCircle, AlertCircle, X, Info, TrendingUp, List, FileText, Sun, Moon } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Classification badge colors - works for both themes
const classificationStyles = {
  "Low Income": { bg: "bg-red-500/20", text: "text-red-600 dark:text-red-400", border: "border-red-500/50", icon: "🔴" },
  "Lower-Middle": { bg: "bg-orange-500/20", text: "text-orange-600 dark:text-orange-400", border: "border-orange-500/50", icon: "🟠" },
  "Middle": { bg: "bg-yellow-500/20", text: "text-yellow-600 dark:text-yellow-400", border: "border-yellow-500/50", icon: "🟡" },
  "Middle Income": { bg: "bg-yellow-500/20", text: "text-yellow-600 dark:text-yellow-400", border: "border-yellow-500/50", icon: "🟡" },
  "Upper-Middle": { bg: "bg-blue-500/20", text: "text-blue-600 dark:text-blue-400", border: "border-blue-500/50", icon: "🔵" },
  "High Income": { bg: "bg-green-500/20", text: "text-green-600 dark:text-green-400", border: "border-green-500/50", icon: "🟢" },
};

// Parse JSON from response text
const parseAnalysisResult = (resultText) => {
  if (!resultText) return null;
  
  try {
    const jsonMatch = resultText.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1]);
    }
    
    const jsonStart = resultText.indexOf('{');
    const jsonEnd = resultText.lastIndexOf('}');
    if (jsonStart !== -1 && jsonEnd !== -1) {
      const jsonStr = resultText.substring(jsonStart, jsonEnd + 1);
      return JSON.parse(jsonStr);
    }
    
    return null;
  } catch (e) {
    console.error("Failed to parse JSON:", e);
    return null;
  }
};

// Get classification style
const getClassificationStyle = (classification) => {
  if (!classification) return classificationStyles["Middle"];
  
  for (const key of Object.keys(classificationStyles)) {
    if (classification.toLowerCase().includes(key.toLowerCase())) {
      return classificationStyles[key];
    }
  }
  return classificationStyles["Middle"];
};

function App() {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [context, setContext] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setDarkMode(savedTheme === 'dark');
    }
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');
  };

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setError(null);
    setResults([]);
    
    const newPreviews = selectedFiles.map(file => ({
      name: file.name,
      url: URL.createObjectURL(file)
    }));
    setPreviews(newPreviews);
  };

  // Remove a file
  const removeFile = (index) => {
    const newFiles = [...files];
    const newPreviews = [...previews];
    URL.revokeObjectURL(newPreviews[index].url);
    newFiles.splice(index, 1);
    newPreviews.splice(index, 1);
    setFiles(newFiles);
    setPreviews(newPreviews);
    setResults([]);
  };

  // Handle drag and drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type.startsWith('image/')
    );
    if (droppedFiles.length > 0) {
      setFiles(droppedFiles);
      setError(null);
      setResults([]);
      const newPreviews = droppedFiles.map(file => ({
        name: file.name,
        url: URL.createObjectURL(file)
      }));
      setPreviews(newPreviews);
    }
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Analyze images
  const analyzeImages = async () => {
    if (files.length === 0) {
      setError("Please upload at least one image");
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const analysisResults = [];
      
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        if (context) {
          formData.append("context", context);
        }

        const response = await fetch(`${API}/analyze`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        analysisResults.push(data);
      }

      setResults(analysisResults);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Render parsed result
  const renderParsedResult = (result) => {
    const parsed = parseAnalysisResult(result.result);
    
    if (parsed) {
      const style = getClassificationStyle(parsed.classification);
      
      return (
        <div className="space-y-4">
          {/* Classification Header */}
          <div className={`${style.bg} ${style.border} border rounded-xl p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{style.icon}</span>
                <div>
                  <h4 className={`text-lg font-bold ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                    {parsed.classification}
                  </h4>
                  <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Desil {parsed.desil_range}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                  {parsed.confidence_percentage}%
                </div>
                <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-600'}`}>Confidence: {parsed.confidence}</p>
              </div>
            </div>
          </div>

          {/* Key Observations */}
          {parsed.key_observations && parsed.key_observations.length > 0 && (
            <div className={`rounded-xl p-4 ${darkMode ? 'bg-slate-700/30' : 'bg-slate-100'}`}>
              <h5 className={`font-semibold mb-3 flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                <List className="w-4 h-4 text-emerald-500" />
                Key Observations
              </h5>
              <ul className="space-y-2">
                {parsed.key_observations.map((obs, idx) => (
                  <li key={idx} className={`flex items-start gap-2 text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                    <span className="text-emerald-500 mt-1">•</span>
                    <span>{obs}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Reasoning */}
          {parsed.detailed_reasoning && (
            <div className={`rounded-xl p-4 ${darkMode ? 'bg-slate-700/30' : 'bg-slate-100'}`}>
              <h5 className={`font-semibold mb-3 flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                <FileText className="w-4 h-4 text-blue-500" />
                Detailed Analysis
              </h5>
              <p className={`text-sm leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                {parsed.detailed_reasoning}
              </p>
            </div>
          )}
        </div>
      );
    }
    
    // Fallback: show raw text if JSON parsing fails
    return (
      <div 
        className={`text-sm leading-relaxed whitespace-pre-wrap ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}
        dangerouslySetInnerHTML={{ 
          __html: result.result
            .replace(/\*\*(.*?)\*\*/g, `<strong class="${darkMode ? 'text-white' : 'text-slate-900'}">$1</strong>`)
            .replace(/\n/g, '<br/>')
        }}
      />
    );
  };

  // Theme classes
  const themeClasses = {
    bg: darkMode ? 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900' : 'bg-gradient-to-br from-slate-100 via-white to-slate-100',
    header: darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white/80 border-slate-200',
    card: darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200 shadow-sm',
    text: darkMode ? 'text-white' : 'text-slate-900',
    textMuted: darkMode ? 'text-slate-400' : 'text-slate-600',
    input: darkMode ? 'bg-slate-700/50 border-slate-600 text-white placeholder-slate-500' : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400',
    dropzone: darkMode ? 'border-slate-600 hover:border-emerald-500' : 'border-slate-300 hover:border-emerald-500',
    resultCard: darkMode ? 'bg-slate-700/30 border-slate-600' : 'bg-slate-50 border-slate-200',
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg}`}>
      {/* Header */}
      <header className={`backdrop-blur-sm border-b sticky top-0 z-10 ${themeClasses.header}`}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-500/20 rounded-lg">
                <Home className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <h1 className={`text-xl font-bold ${themeClasses.text}`}>House Socioeconomic Analyzer</h1>
                <p className={`text-sm ${themeClasses.textMuted}`}>AI-powered housing assessment for Indonesia</p>
              </div>
            </div>
            
            {/* Theme Toggle Button */}
            <button
              data-testid="theme-toggle"
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${darkMode ? 'bg-slate-700 hover:bg-slate-600 text-yellow-400' : 'bg-slate-200 hover:bg-slate-300 text-slate-700'}`}
              aria-label="Toggle theme"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Upload */}
          <div className="space-y-6">
            {/* Upload Section */}
            <div className={`backdrop-blur-sm rounded-2xl border p-6 ${themeClasses.card}`}>
              <h2 className={`text-lg font-semibold mb-4 flex items-center gap-2 ${themeClasses.text}`}>
                <Upload className="w-5 h-5 text-emerald-500" />
                Upload House Images
              </h2>
              
              {/* Dropzone */}
              <div
                data-testid="dropzone"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${themeClasses.dropzone}`}
                onClick={() => document.getElementById('fileInput').click()}
              >
                <Upload className={`w-12 h-12 mx-auto mb-4 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`} />
                <p className={`mb-2 ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>Drag & drop images here</p>
                <p className={`text-sm ${darkMode ? 'text-slate-500' : 'text-slate-500'}`}>or click to browse</p>
                <p className={`text-xs mt-2 ${darkMode ? 'text-slate-600' : 'text-slate-400'}`}>PNG, JPG, JPEG, WEBP</p>
                <input
                  id="fileInput"
                  data-testid="file-input"
                  type="file"
                  multiple
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              {/* Image Previews */}
              {previews.length > 0 && (
                <div className="mt-6">
                  <h3 className={`text-sm font-medium mb-3 ${themeClasses.textMuted}`}>
                    Uploaded Images ({previews.length})
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    {previews.map((preview, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={preview.url}
                          alt={preview.name}
                          className={`w-full h-24 object-cover rounded-lg border ${darkMode ? 'border-slate-600' : 'border-slate-300'}`}
                        />
                        <button
                          data-testid={`remove-image-${index}`}
                          onClick={() => removeFile(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                        <p className={`text-xs truncate mt-1 ${themeClasses.textMuted}`}>{preview.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Context Input */}
              <div className="mt-6">
                <label className={`text-sm font-medium mb-2 block ${themeClasses.textMuted}`}>
                  Additional Context (Optional)
                </label>
                <textarea
                  data-testid="context-input"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="E.g., 'House in rural Java' or 'Front view of the property'"
                  className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none ${themeClasses.input}`}
                  rows={3}
                />
              </div>

              {/* Analyze Button */}
              <button
                data-testid="analyze-button"
                onClick={analyzeImages}
                disabled={files.length === 0 || loading}
                className="w-full mt-6 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-500 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    Analyze House
                  </>
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div data-testid="error-message" className="mt-4 bg-red-500/20 border border-red-500 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-red-500 text-sm">{error}</p>
                </div>
              )}
            </div>

            {/* Info Card */}
            <div className={`backdrop-blur-sm rounded-2xl border p-6 ${themeClasses.card}`}>
              <h3 className={`text-sm font-semibold mb-3 flex items-center gap-2 ${themeClasses.text}`}>
                <Info className="w-4 h-4 text-blue-500" />
                Classification Categories
              </h3>
              <div className="space-y-2">
                {[
                  { label: "Low Income", desil: "Desil 1-2", color: "bg-red-500" },
                  { label: "Lower-Middle", desil: "Desil 3-4", color: "bg-orange-500" },
                  { label: "Middle Income", desil: "Desil 5-6", color: "bg-yellow-500" },
                  { label: "Upper-Middle", desil: "Desil 7-8", color: "bg-blue-500" },
                  { label: "High Income", desil: "Desil 9-10", color: "bg-green-500" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                    <span className={`text-sm ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>{item.label}</span>
                    <span className={`text-xs ${themeClasses.textMuted}`}>({item.desil})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <div className={`backdrop-blur-sm rounded-2xl border p-6 min-h-[400px] ${themeClasses.card}`}>
              <h2 className={`text-lg font-semibold mb-4 flex items-center gap-2 ${themeClasses.text}`}>
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                Analysis Results
              </h2>
              
              {results.length === 0 && !loading && (
                <div className={`flex flex-col items-center justify-center h-64 ${themeClasses.textMuted}`}>
                  <Home className="w-16 h-16 mb-4 opacity-50" />
                  <p>Upload images to see analysis results</p>
                </div>
              )}

              {loading && (
                <div className="flex flex-col items-center justify-center h-64">
                  <Loader2 className="w-12 h-12 text-emerald-500 animate-spin mb-4" />
                  <p className={themeClasses.textMuted}>Analyzing house images...</p>
                  <p className={`text-sm mt-2 ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>This may take a moment</p>
                </div>
              )}

              {results.length > 0 && (
                <div className="space-y-6">
                  {results.map((result, index) => (
                    <div
                      key={index}
                      data-testid={`result-card-${index}`}
                      className={`rounded-xl p-5 border ${themeClasses.resultCard}`}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h3 className={`font-medium flex items-center gap-2 ${themeClasses.text}`}>
                          <FileText className={`w-4 h-4 ${themeClasses.textMuted}`} />
                          {result.filename}
                        </h3>
                        {result.success ? (
                          <CheckCircle className="w-5 h-5 text-emerald-500" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-500" />
                        )}
                      </div>
                      
                      {result.success ? (
                        renderParsedResult(result)
                      ) : (
                        <div className="bg-red-500/20 rounded-lg p-4">
                          <p className="text-red-500 text-sm">{result.error}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className={`border-t mt-12 py-6 ${darkMode ? 'border-slate-700' : 'border-slate-200'}`}>
        <p className={`text-center text-sm ${themeClasses.textMuted}`}>
          Built with React + Gemini Vision AI | For Educational Purposes
        </p>
      </footer>
    </div>
  );
}

export default App;
