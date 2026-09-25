import "dotenv/config";
import mongoose from "mongoose";

export const connectDb = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      dbName: process.env.DB_NAME || "news_pulse",
    });
    console.log("db connected");
    return conn;
  } catch (error) {
    console.error({ error: error });
    process.exit();
  }
};
