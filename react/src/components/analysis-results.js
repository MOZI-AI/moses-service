import React from "react";
import { Row, Col, message, Alert } from "antd";
import { AnalysisStatus, SERVER_ADDRESS } from "../utils";
import { Result } from "./result";
import { Loader } from "./loader";

export class AnalysisResults extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      analysisId: null,
      analysisProgress: 0,
      analysisStatus: null,
      analysisStartTime: null,
      analysisEndTime: null,
      analysisStatusMessage: null
    };
  }

  componentDidMount() {
    const id = this.getQueryVariable("id");
    if (!id) {
      return;
    }
    fetch(SERVER_ADDRESS + "status/" + id)
      .then(response => response.json())
      .then(response => {
        this.setState({
          analysisId: id,
          analysisStatus: response.status,
          analysisProgress: response.progress,
          analysisStartTime: response.start_time,
          analysisEndTime: response.end_time,
          analysisStatusMessage: response.message
        });
      });
  }

  componentWillUpdate(nextProps, nextState) {
    if (nextState.analysisStatus !== this.state.analysisStatus) {
      if (nextState.analysisStatus === AnalysisStatus.ERROR) {
        message.error("Analysis run into an error.");
      } else if (nextState.analysisStatus === AnalysisStatus.COMPLETED) {
        message.success("Analysis completed successfully!");
      }
    }
  }

  downloadResult() {
    window.open(
      SERVER_ADDRESS + "result/" + this.getQueryVariable("id"),
      "_blank"
    );
  }

  getQueryVariable(variable) {
    const vars = window.location.search.substring(1).split("&");
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split("=");
      if (pair[0] == variable) {
        return pair[1];
      }
    }
    return null;
  }

  render() {
    const progressProps = {
      progress: this.state.analysisProgress,
      status: this.state.analysisStatus,
      start: this.state.analysisStartTime,
      end: this.state.analysisEndTime,
      message: this.state.message,
      downloadResult: this.downloadResult
    };

    return (
      <React.Fragment>
        <Row type="flex" justify="center" style={{paddingTop: '30px'}}>
          <Col span={8} style={{ textAlign: "center" }}>          
            {this.state.analysisStatus ? (
              <Result {...progressProps} />
            ) : this.state.id? (
              <Loader />
            ): <Alert type="warning" message="It seems there is a problem with your request. Please make sure the URL is correct." />}
          </Col>
        </Row>
      </React.Fragment>
    );
  }
}
