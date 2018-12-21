export const AnalysisStatus = {
  ACTIVE: 1,
  COMPLETED: 2,
  ERROR: -1
};

export const SERVER_ADDRESS =
  process.env.SERVICE_ADDR || "http://localhost:5000/";

export const getQueryValue = variable => {
  const vars = window.location.search.substring(1).split("&");
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split("=");
    if (pair[0] == variable) {
      return pair[1];
    }
  }
  return null;
};

export const fetchAnalysisStatus = id => {
  return fetch(SERVER_ADDRESS + "status/" + id).then(response =>
    response.json()
  );
};
