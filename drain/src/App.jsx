import { useState } from "react";
import DragDropArea from "./components/DragDropArea";
import "./App.css";
import Banner from "./components/Banner";

const TiffResult = ({
  fileName,
  spellcheckedText,
  analysisResult,
  extractedInfo,
}) => (
  <div className="results-container">
    <h3>{fileName}</h3>
    <div className="result-box">
      <h4>Spellchecked Text:</h4>
      <p>{spellcheckedText}</p>
    </div>
    <div className="result-box">
      <h4>Analysis Result:</h4>
      <p>
        {analysisResult ? (
          <span className="racist-label">Racist Content Detected</span>
        ) : (
          <span className="non-racist-label">No Racist Content</span>
        )}
      </p>
    </div>
    {(extractedInfo.names.length > 0 || extractedInfo.locations.length > 0) && (
      <div className="result-box">
        <h4>Extracted Information:</h4>
        {extractedInfo.names.length > 0 && (
          <div>
            <h5>Names:</h5>
            <ul>
              {extractedInfo.names.map((name, index) => (
                <li key={index}>{name}</li>
              ))}
            </ul>
          </div>
        )}
        {extractedInfo.locations.length > 0 && (
          <div>
            <h5>Locations:</h5>
            <ul>
              {extractedInfo.locations.map((location, index) => (
                <li key={index}>{location}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )}
  </div>
);

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [ocrEngine, setOcrEngine] = useState("google");
  const [analysisMethod, setAnalysisMethod] = useState("logistic_regression");
  const [results, setResults] = useState([]);

  const handleFileUpload = async (files) => {
    setResults([]);
    setIsLoading(true);

    try {
      const newResults = [];
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("ocr_engine", ocrEngine);
        formData.append("analysis_method", analysisMethod);

        const response = await fetch("http://127.0.0.1:5000/api/upload", {
          method: "POST",
          body: formData,
        });

        console.log(response);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        newResults.push({
          fileName: file.name,
          spellcheckedText: data.spellchecked_text || "No text available",
          analysisResult: data.result || false,
          extractedInfo: data.extracted_info || { names: [], locations: [] },
        });
      }
      setResults(newResults);
    } catch (error) {
      console.error("Error during fetch:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadExcel = async () => {
    const response = await fetch('http://127.0.0.1:5000/api/download_excel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(results)
    });

    if (response.ok) {
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = 'analysis_results.xlsx';
      document.body.appendChild(link);
      link.click();
      link.remove();
    } else {
      console.error('Failed to download file:', await response.text());
    }
};

  const handleOcrChange = (event) => {
    setOcrEngine(event.target.value);
  };

  const handleAnalysisChange = (event) => {
    setAnalysisMethod(event.target.value);
  };

  return (
    <div className="App">
      <Banner />
      <header className="App-header">
        <h1>
          DRAIN: Deed Restriction Artificial Intelligence Notification System
        </h1>
        <h3>OCR File Upload</h3>
        <p>Convert your files to text using OCR</p>

        <DragDropArea onFileUpload={handleFileUpload} isLoading={isLoading} />

        <div className="selector-container">
          <div className="select-box">
            <label htmlFor="ocr-select">Select OCR Engine: </label>
            <select
              id="ocr-select"
              value={ocrEngine}
              onChange={handleOcrChange}
              className="select-input"
            >
              <option value="google">Google OCR</option>
            </select>
          </div>

          <div className="select-box">
            <label htmlFor="analysis-select">Select Analysis Method: </label>
            <select
              id="analysis-select"
              value={analysisMethod}
              onChange={handleAnalysisChange}
              className="select-input"
            >
              <option value="chatgpt">ChatGPT</option>
              <option value="logistic_regression">Logistic Regression</option>
            </select>
          </div>
        </div>
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <>
            {results.map((result, index) => (
              <TiffResult
                key={index}
                fileName={result.fileName}
                spellcheckedText={result.spellcheckedText}
                analysisResult={result.analysisResult}
                extractedInfo={result.extractedInfo}
              />
            ))}
            {results.length > 0 && (
              <button onClick={handleDownloadExcel} className="download-button">Download Results as Excel</button>
            )}
          </>
        )}
      </header>
    </div>
  );
};

export default App;
