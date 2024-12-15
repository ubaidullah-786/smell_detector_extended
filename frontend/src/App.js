import React, { useState } from "react";
import UploadFile from "./components/UploadFile";
import Results from "./components/Results";

const App = () => {
  const [results, setResults] = useState(null);

  return (
    <div
      style={{
        textAlign: "center",
      }}
    >
      <h1 style={{ fontSize: "48px", marginTop: "10px", marginBottom: 0 }}>
        Python Code Smell Detector
      </h1>
      <UploadFile onResults={setResults} />
      <Results results={results} />
    </div>
  );
};

export default App;
