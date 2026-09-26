import express from "express";
import cors from "cors";
import { connectDb } from "./src/db/index.js";
import clusterRouter from "./src/routes/cluster.router.js";
import ingestRouter from "./src/routes/ingest.router.js";
import timelineRouter from "./src/routes/timeline.router.js";

const app = express();
const allowedOrigins = (
  process.env.CORS_ORIGIN || "http://localhost:5173,http://127.0.0.1:5173"
)
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }
      callback(null, false);
    },
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);
app.use(express.json({ limit: "16kb" }));
app.use(express.urlencoded({ extended: true, limit: "16kb" }));
app.get("/health", (_request, response) => response.json({ status: "ok" }));
app.use("/clusters", clusterRouter);
app.use("/timeline", timelineRouter);
app.use("/ingest", ingestRouter);

app.use((error, _request, response, _next) => {
  console.error(error);
  response.status(500).json({ error: "Internal server error" });
});

const port = Number(process.env.PORT) || 3000;

connectDb().then(() => {
  app.listen(port, () => {
    console.log(`API listening on port ${port}`);
  });
});

export default app;
