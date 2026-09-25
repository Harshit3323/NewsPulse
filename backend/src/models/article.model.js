import mongoose from "mongoose";

const articleSchema = new mongoose.Schema(
  {
    id: {
      type: String,
      required: true,
      unique: true,
      index: true,
      trim: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    summary: {
      type: String,
      default: "",
    },
    link: {
      type: String,
      required: true,
      trim: true,
    },
    published: {
      type: Date,
      default: null,
    },
    source: {
      type: String,
      required: true,
      trim: true,
      index: true,
    },
    full_text: {
      type: String,
      default: "",
    },
  },
  {
    collection: "articles",
  },
);

export const Article = mongoose.model("Article", articleSchema);
export default Article;
