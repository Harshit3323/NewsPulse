import Article from "../models/article.model.js";
import Cluster from "../models/cluster.model.js";

export const getClusters = async (_request, response) => {
  const clusters = await Cluster.find()
    .sort({ start_time: -1, cluster_id: 1 })
    .lean();

  response.json(clusters);
};

export const getClusterById = async (request, response) => {
  const clusterId = Number(request.params.id);

  if (!Number.isInteger(clusterId)) {
    return response
      .status(400)
      .json({ error: "Cluster id must be an integer" });
  }

  const cluster = await Cluster.findOne({ cluster_id: clusterId }).lean();

  if (!cluster) {
    return response.status(404).json({ error: "Cluster not found" });
  }

  const articles = await Article.find({ id: { $in: cluster.article_ids } })
    .sort({ published: 1 })
    .lean();

  response.json({ ...cluster, articles });
};
