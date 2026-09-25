import Cluster from "../models/cluster.model.js";

export const getTimeline = async (_request, response) => {
  const clusters = await Cluster.find()
    .sort({ start_time: 1, cluster_id: 1 })
    .lean();

  response.json(
    clusters.map((cluster) => ({
      cluster_id: cluster.cluster_id,
      label: cluster.label,
      start_time: cluster.start_time,
      end_time: cluster.end_time,
      article_count: cluster.article_count,
      intensity: cluster.article_count,
    })),
  );
};
