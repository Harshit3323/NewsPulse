import {
  getJobStatus,
  triggerIngest as triggerIngestJob,
} from "../services/ingest.service.js";

export const triggerIngest = async (_request, response) => {
  const job = await triggerIngestJob();
  response.status(202).json(job);
};

export const getIngestStatus = async (request, response) => {
  const job = await getJobStatus(request.params.jobId);

  if (!job) {
    return response.status(404).json({ error: "Ingest job not found" });
  }

  response.json(job);
};
