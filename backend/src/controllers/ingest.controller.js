import { getIngestJob, startIngestJob } from "../services/ingest.service.js";

export const triggerIngest = (_request, response) => {
  const job = startIngestJob();
  response.status(202).json(job);
};

export const getIngestStatus = (request, response) => {
  const job = getIngestJob(request.params.jobId);

  if (!job) {
    return response.status(404).json({ error: "Ingest job not found" });
  }

  response.json(job);
};
