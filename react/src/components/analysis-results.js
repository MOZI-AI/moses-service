import React from "react";
import {
  Button,
  Icon,
  Alert,
  Row,
  Col,
  message,
  Progress,
  Spin,
  Collapse
} from "antd";
import { AnalysisStatus, SERVER_ADDRESS } from "../utils";
import * as moment from "moment";

export class AnalysisResults extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      analysisProgress: 0,
      analysisStatus: null,
      analysisStartTime: null,
      analysisEndTime: null,
      analysisStatusMessage: null
    };
  }

  componentDidMount() {
    fetch(SERVER_ADDRESS + "status/" + window.location.href.split("?id=").pop())
      .then(response => response.json())
      .then(response => {
        this.setState({
          analysisStatus: response.status,
          analysisProgress: response.progress,
          analysisStartTime: response.start_time,
          analysisEndTime: response.end_time,
          analysisStatusMessage: response.message
        });
      });
  }

  componentDidUpdate() {
    console.log(this.state);
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
      SERVER_ADDRESS + "result/" + window.location.href.split("/").pop(),
      "_blank"
    );
  }

  renderLoader() {
    return (
      <React.Fragment>
        <Spin style={{ marginRight: "15px" }} />{" "}
        <span> Fetching results ...</span>
      </React.Fragment>
    );
  }

  renderResults() {
    const {
      analysisProgress,
      analysisStatus,
      analysisStartTime,
      analysisEndTime
    } = this.state;
    const progressAttributes = {
      percent: analysisProgress
    };
    if (analysisStatus === AnalysisStatus.ACTIVE) {
      progressAttributes["status"] = "active";
    } else if (analysisStatus === AnalysisStatus.ERROR) {
      progressAttributes["status"] = "exception";
    }

    return (
      <React.Fragment>
        <img src="assets/mozi_globe.png" style={{ width: "100px" }} />
        <h2 style={{ marginBottom: "30px" }}>Mozi service results</h2>

        {analysisStatus === AnalysisStatus.ACTIVE && (
          <span>
            Analysis started
            {" " + moment(analysisStartTime * 1000).fromNow()}
          </span>
        )}

        {analysisStatus === AnalysisStatus.COMPLETED && (
          <span>
            Analysis completed after
            {" " +
              moment
                .duration(
                  moment(analysisEndTime).diff(moment(analysisStartTime))
                )
                .humanize()}
          </span>
        )}

        {analysisStatus !== AnalysisStatus.ERROR && (
          <Progress {...progressAttributes} style={{ marginBottom: "15px" }} />
        )}

        {analysisStatus === AnalysisStatus.ACTIVE && (
          <p>
            The analysis might take a while depending on the size of the dataset
            and analysis parameter values.
          </p>
        )}
        {analysisStatus === AnalysisStatus.COMPLETED && (
          <Button type="primary" onClick={this.downloadResult}>
            <Icon type="download" />
            Download analysis results
          </Button>
        )}
        {analysisStatus === AnalysisStatus.ERROR && (
          <Alert
            justify="left"
            type="error"
            message={
              "Analysis failed after " +
              moment
                .duration(
                  moment(analysisEndTime).diff(moment(analysisStartTime))
                )
                .humanize()
            }
            description={
              <Collapse
                bordered={false}
                style={{
                  background: "none",
                  boxShadow: "none",
                  textAlign: "left"
                }}
              >
                <Collapse.Panel
                  style={{ backgroundColor: "#f8d8d7" }}
                  header="Show stacktrace"
                  key="1"
                >
                  {this.state.analysisStatusMessage}
                </Collapse.Panel>
              </Collapse>
            }
          />
        )}
      </React.Fragment>
    );
  }

  render() {
    return (
      <React.Fragment>
        <Row type="flex" justify="center" style={{ padding: "75px" }}>
          <Col span={8} style={{ textAlign: "center" }}>
            {this.state.analysisStatus
              ? this.renderResults()
              : this.renderLoader()}
          </Col>
        </Row>
      </React.Fragment>
    );
  }
}
