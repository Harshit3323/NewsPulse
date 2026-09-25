import { Router } from "express";
import {
  getIngestStatus,
  triggerIngest,
} from "../controllers/ingest.controller.js";

const router = Router();

router.post("/trigger", triggerIngest);
router.get("/status/:jobId", getIngestStatus);

export default router;
