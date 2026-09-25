import { Router } from "express";
import {
  getClusterById,
  getClusters,
} from "../controllers/cluster.controller.js";

const router = Router();

router.get("/", getClusters);
router.get("/:id", getClusterById);

export default router;
