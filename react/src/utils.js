export const AnalysisStatus = {
  ACTIVE: 1,
  COMPLETED: 2,
  ERROR: -1
};

export const SERVER_ADDRESS =
  process.env.SERVICE_ADDR || "http://localhost:5000/";
