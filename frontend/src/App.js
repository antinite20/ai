import React, { useState, useCallback } from "react";
import "@/App.css";
import { Upload, Home, Loader2, CheckCircle, AlertCircle, X, Info } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Classification badge colors
const classificationColors = {
  "Low Income": "bg-red-100 text-red-800 border-red-300",
  "Lower-Middle": "bg-orange-100 text-orange-800 border-orange-300",
  "Middle": "bg-yellow-100 text-yellow-800 border-yellow-300",
  "Upper-Middle": "bg-blue-100 text-blue-800 border-blue-300",
  "High Income": "bg-green-100 text-green-800 border-green-300",
};

function App() {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [context, setContext] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setError(null);
    setResults([]);
    
    // Create previews
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

  // Parse classification from result text
  const getClassification = (resultText) => {
    if (!resultText) return null;
    const patterns = ["Low Income", "Lower-Middle", "Middle Income", "Upper-Middle", "High Income"];
    for (const pattern of patterns) {
      if (resultText.includes(pattern)) {
        return pattern === "Middle Income" ? "Middle" : pattern;
      }
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/20 rounded-lg">
              <Home className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">House Socioeconomic Analyzer</h1>
              <p className="text-sm text-slate-400">AI-powered housing assessment for Indonesia</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Upload */}
          <div className="space-y-6">
            {/* Upload Section */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-emerald-400" />
                Upload House Images
              </h2>
              
              {/* Dropzone */}
              <div
                data-testid="dropzone"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center hover:border-emerald-500 transition-colors cursor-pointer"
                onClick={() => document.getElementById('fileInput').click()}
              >
                <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                <p className="text-slate-300 mb-2">Drag & drop images here</p>
                <p className="text-slate-500 text-sm">or click to browse</p>
                <p className="text-slate-600 text-xs mt-2">PNG, JPG, JPEG, WEBP</p>
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
                  <h3 className="text-sm font-medium text-slate-300 mb-3">
                    Uploaded Images ({previews.length})
                  </h3>
                  <div className="grid grid-cols-3 gap-3">
                    {previews.map((preview, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={preview.url}
                          alt={preview.name}
                          className="w-full h-24 object-cover rounded-lg border border-slate-600"
                        />
                        <button
                          data-testid={`remove-image-${index}`}
                          onClick={() => removeFile(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                        <p className="text-xs text-slate-400 truncate mt-1">{preview.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Context Input */}
              <div className="mt-6">
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Additional Context (Optional)
                </label>
                <textarea
                  data-testid="context-input"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="E.g., 'House in rural Java' or 'Front view of the property'"
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
                  rows={3}
                />
              </div>

              {/* Analyze Button */}
              <button
                data-testid="analyze-button"
                onClick={analyzeImages}
                disabled={files.length === 0 || loading}
                className="w-full mt-6 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Analyze House
                  </>
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div data-testid="error-message" className="mt-4 bg-red-500/20 border border-red-500 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}
            </div>

            {/* Info Card */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 p-6">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-400" />
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
                    <span className="text-slate-300 text-sm">{item.label}</span>
                    <span className="text-slate-500 text-xs">({item.desil})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 p-6 min-h-[400px]">
              <h2 className="text-lg font-semibold text-white mb-4">Analysis Results</h2>
              
              {results.length === 0 && !loading && (
                <div className="flex flex-col items-center justify-center h-64 text-slate-500">
                  <Home className="w-16 h-16 mb-4 opacity-50" />
                  <p>Upload images to see analysis results</p>
                </div>
              )}

              {loading && (
                <div className="flex flex-col items-center justify-center h-64">
                  <Loader2 className="w-12 h-12 text-emerald-400 animate-spin mb-4" />
                  <p className="text-slate-400">Analyzing house images...</p>
                  <p className="text-slate-500 text-sm mt-2">This may take a moment</p>
                </div>
              )}

              {results.length > 0 && (
                <div className="space-y-6">
                  {results.map((result, index) => {
                    const classification = getClassification(result.result);
                    const colorClass = classification ? classificationColors[classification] : "bg-slate-100 text-slate-800";
                    
                    return (
                      <div
                        key={index}
                        data-testid={`result-card-${index}`}
                        className="bg-slate-700/30 rounded-xl p-5 border border-slate-600"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-white font-medium">{result.filename}</h3>
                          {result.success ? (
                            <CheckCircle className="w-5 h-5 text-emerald-400" />
                          ) : (
                            <AlertCircle className="w-5 h-5 text-red-400" />
                          )}
                        </div>
                        
                        {result.success ? (
                          <div className="space-y-4">
                            {classification && (
                              <div className="flex items-center gap-2">
                                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${colorClass}`}>
                                  {classification}
                                </span>
                              </div>
                            )}
                            <div 
                              className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap prose prose-invert prose-sm max-w-none"
                              dangerouslySetInnerHTML={{ 
                                __html: result.result
                                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                  .replace(/\n/g, '<br/>')
                              }}
                            />
                          </div>
                        ) : (
                          <p className="text-red-400 text-sm">{result.error}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-12 py-6">
        <p className="text-center text-slate-500 text-sm">
          Built with React + Gemini Vision AI | For Educational Purposes
        </p>
      </footer>
    </div>
  );
}

export default App;
