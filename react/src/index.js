import React from "react";
import ReactDOM from "react-dom";
import { AnalysisResult } from "./components/analysis-result";
import { getQueryValue, fetchAnalysisStatus } from "./utils";

ReactDOM.render(
  <AnalysisResult
    fetchAnalysisStatus={fetchAnalysisStatus}
    analysisId={getQueryValue("id")}
  />,
  document.getElementById("app")
);
