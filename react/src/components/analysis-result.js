import React from "react";
import { Row, Col, message, Alert } from "antd";
import { Result } from "./result";
import { Loader } from "./loader";
import { AnalysisStatus } from "../utils";
import logo from "../assets/mozi_globe.png";

export class AnalysisResult extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      analysisId: null,
      analysisProgress: 0,
      analysisStatus: null,
      analysisStartTime: null,
      analysisEndTime: null,
      analysisStatusMessage: null,
      fetchingResult: false
    };
    this.downloadResult = this.downloadResult.bind(this);
  }

  componentDidMount() {
    const id = this.props.analysisId;
    if (id) {
      this.setState({ analysisId: id, fetchingResult: true });
      this.props.fetchAnalysisStatus(id).then(response => {
        this.setState({
          fetchingResult: false,
          analysisStatus: response.status,
          analysisProgress: response.progress,
          analysisStartTime: response.start_time,
          analysisEndTime: response.end_time,
          analysisStatusMessage: response.message
        });
      });
    }
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
    window.open(SERVER_ADDRESS + "result/" + this.state.analysisId, "_blank");
  }

  render() {
    const progressProps = {
      progress: this.state.analysisProgress,
      status: this.state.analysisStatus,
      start: this.state.analysisStartTime,
      end: this.state.analysisEndTime,
      message: this.state.analysisStatusMessage,
      downloadResult: this.downloadResult
    };

    return (
      <React.Fragment>
        <Row type="flex" justify="center" style={{ paddingTop: "90px" }}>
          <Col span={8} style={{ textAlign: "center" }}>
            <img src={logo} style={{ width: "100px" }} />
            <h2 style={{ marginBottom: "30px" }}>Mozi service results</h2>
            {this.state.analysisStatus ? (
              <Result {...progressProps} />
            ) : this.state.analysisId ? (
              this.state.fetchingResult ? (
                <Loader />
              ) : (
                <Alert
                  id="invalidID"
                  type="error"
                  message={
                    'Session with ID "' +
                    this.state.analysisId +
                    '" could not be found. Please make sure the session ID is correct and try again.'
                  }
                />
              )
            ) : (
              <Alert
                id="missingID"
                type="error"
                message="It seems there is a problem with your request. Please make sure the URL is correct."
              />
            )}
          </Col>
        </Row>
      </React.Fragment>
    );
  }
}
