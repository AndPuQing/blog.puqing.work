const { WakaTimeClient, RANGE } = require("wakatime-client");

const wakatime = new WakaTimeClient(process.env.WAKATIME_API_KEY);

module.exports = async (req, res) => {
  const stats = (await wakatime.getMyStats({ range: RANGE.LAST_7_DAYS })).data;
  res.status(200).send({ languages: stats.languages, editors: stats.editors });
};
