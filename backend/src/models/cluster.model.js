import mongoose from "mongoose";

const clusterSchema = new mongoose.Schema(
  {
    cluster_id: {
      type: Number,
      required: true,
      unique: true,
      index: true,
    },
    label: {
      type: String,
      required: true,
      trim: true,
    },
    article_ids: {
      type: [String],
      required: true,
      default: [],
      index: true,
    },
    start_time: {
      type: Date,
      default: null,
    },
    end_time: {
      type: Date,
      default: null,
    },
    article_count: {
      type: Number,
      required: true,
      min: 0,
    },
  },
  {
    collection: "clusters",
  },
);

export const Cluster = mongoose.model("Cluster", clusterSchema);
export default Cluster;
