import React, { useState, useCallback } from "react";
import "@/App.css";
import { Upload, Home, Loader2, CheckCircle, AlertCircle, X, Info, TrendingUp, List, FileText } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Classification badge colors
const classificationStyles = {
  "Low Income": { bg: "bg-red-500/20", text: "text-red-400", border: "border-red-500/50", icon: "🔴" },
  "Lower-Middle": { bg: "bg-orange-500/20", text: "text-orange-400", border: "border-orange-500/50", icon: "🟠" },
  "Middle": { bg: "bg-yellow-500/20", text: "text-yellow-400", border: "border-yellow-500/50", icon: "🟡" },
  "Middle Income": { bg: "bg-yellow-500/20", text: "text-yellow-400", border: "border-yellow-500/50", icon: "🟡" },
  "Upper-Middle": { bg: "bg-blue-500/20", text: "text-blue-400", border: "border-blue-500/50", icon: "🔵" },
  "High Income": { bg: "bg-green-500/20", text: "text-green-400", border: "border-green-500/50", icon: "🟢" },
};

// Parse JSON from response text
const parseAnalysisResult = (resultText) => {
  if (!resultText) return null;
  
  try {
    // Try to extract JSON from the response
    const jsonMatch = resultText.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1]);
    }
    
    // Try direct JSON parse
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
                  <h4 className={`text-lg font-bold ${style.text}`}>
                    {parsed.classification}
                  </h4>
                  <p className="text-slate-400 text-sm">Desil {parsed.desil_range}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold ${style.text}`}>
                  {parsed.confidence_percentage}%
                </div>
                <p className="text-slate-400 text-xs">Confidence: {parsed.confidence}</p>
              </div>
            </div>
          </div>

          {/* Key Observations */}
          {parsed.key_observations && parsed.key_observations.length > 0 && (
            <div className="bg-slate-700/30 rounded-xl p-4">
              <h5 className="text-white font-semibold mb-3 flex items-center gap-2">
                <List className="w-4 h-4 text-emerald-400" />
                Key Observations
              </h5>
              <ul className="space-y-2">
                {parsed.key_observations.map((obs, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-300 text-sm">
                    <span className="text-emerald-400 mt-1">•</span>
                    <span>{obs}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Reasoning */}
          {parsed.detailed_reasoning && (
            <div className="bg-slate-700/30 rounded-xl p-4">
              <h5 className="text-white font-semibold mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                Detailed Analysis
              </h5>
              <p className="text-slate-300 text-sm leading-relaxed">
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
        className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap"
        dangerouslySetInnerHTML={{ 
          __html: result.result
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
            .replace(/\n/g, '<br/>')
        }}
      />
    );
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
                    <TrendingUp className="w-5 h-5" />
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
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
                Analysis Results
              </h2>
              
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
                  {results.map((result, index) => (
                    <div
                      key={index}
                      data-testid={`result-card-${index}`}
                      className="bg-slate-700/30 rounded-xl p-5 border border-slate-600"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-white font-medium flex items-center gap-2">
                          <FileText className="w-4 h-4 text-slate-400" />
                          {result.filename}
                        </h3>
                        {result.success ? (
                          <CheckCircle className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-400" />
                        )}
                      </div>
                      
                      {result.success ? (
                        renderParsedResult(result)
                      ) : (
                        <div className="bg-red-500/20 rounded-lg p-4">
                          <p className="text-red-400 text-sm">{result.error}</p>
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
      <footer className="border-t border-slate-700 mt-12 py-6">
        <p className="text-center text-slate-500 text-sm">
          Built with React + Gemini Vision AI | For Educational Purposes
        </p>
      </footer>
    </div>
  );
}

export default App;
