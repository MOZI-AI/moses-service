import React from "react";
import { AnalysisStatus } from "../utils";
import { shallow } from "enzyme";
import { AnalysisResult } from "../components/analysis-result";

describe("<AnalysisResult>", () => {
  it("shows error if analysis ID is missing", () => {
    const wrapper = shallow(<AnalysisResult analysisId={null} />);
    expect(wrapper.find("Alert#missingID").exists()).toBeTruthy();
  });

  it("shows error if analysis ID is invalid", () => {
    const mockResponse = new Promise((resolve, reject) =>
      resolve({
        response: "Session not found"
      })
    );

    const wrapper = shallow(
      <AnalysisResult analysisId="X" fetchAnalysisStatus={id => mockResponse} />
    );
    mockResponse.then(response => {
      expect(wrapper.find("Alert#invalidID").exists()).toBeTruthy();
    });
  });

  it("shows loader if fetching analysis result", () => {
    const wrapper = shallow(
      <AnalysisResult
        analysisId="X"
        fetchAnalysisStatus={() =>
          new Promise((resolve, reject) => {
            setTimeout(function() {
              resolve({
                analysisStatus: AnalysisStatus.ERROR,
                progress: 0,
                start_time: null,
                end_time: null,
                message: null
              });
            }, 10000);
          })
        }
      />
    );
    expect(wrapper.find("Loader").exists()).toBeTruthy();
  });
});
