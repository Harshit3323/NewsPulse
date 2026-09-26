import { randomUUID } from "node:crypto";
const jobs = new Map();
const githubApiUrl = "https://api.github.com";

const githubHeaders = () => ({
  Accept: "application/vnd.github+json",
  Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
  "X-GitHub-Api-Version": "2022-11-28",
});

const workflowPath = async () => {
  const { GITHUB_OWNER, GITHUB_REPO, GITHUB_WORKFLOW_FILE } = process.env;
  if (
    !process.env.GITHUB_TOKEN ||
    !GITHUB_OWNER ||
    !GITHUB_REPO ||
    !GITHUB_WORKFLOW_FILE
  ) {
    throw new Error(
      "GitHub Actions ingest is not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, and GITHUB_WORKFLOW_FILE.",
    );
  }

  const repoWorkflowPath = `/repos/${encodeURIComponent(GITHUB_OWNER)}/${encodeURIComponent(GITHUB_REPO)}/actions/workflows`;
  const { workflows = [] } = await githubRequest(repoWorkflowPath);
  const workflow = workflows.find((candidate) => {
    const candidateFile = candidate.path || candidate.file_name || "";
    const candidateName = candidate.name || "";
    return (
      candidateFile.endsWith(`/${GITHUB_WORKFLOW_FILE}`) ||
      candidateFile === GITHUB_WORKFLOW_FILE ||
      candidateName === GITHUB_WORKFLOW_FILE ||
      candidateName === "News Pulse Scraper"
    );
  });

  if (!workflow) {
    throw new Error(
      `GitHub workflow ${GITHUB_WORKFLOW_FILE} was not found in ${GITHUB_OWNER}/${GITHUB_REPO}.`,
    );
  }

  return {
    workflowId: workflow.id,
    workflowUrl: `/repos/${encodeURIComponent(GITHUB_OWNER)}/${encodeURIComponent(GITHUB_REPO)}/actions/workflows/${workflow.id}`,
  };
};

const githubRequest = async (url, options = {}) => {
  const response = await fetch(`${githubApiUrl}${url}`, {
    ...options,
    headers: { ...githubHeaders(), ...options.headers },
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body.message) detail = body.message;
    } catch {
      // Keep the HTTP status text when GitHub does not return a JSON error body.
    }
    throw new Error(`GitHub API request failed: ${detail}`);
  }

  return response.status === 204 ? undefined : response.json();
};

const publicJob = ({
  runId: _runId,
  workflowUrl: _workflowUrl,
  dispatchRequestedAt: _dispatchRequestedAt,
  ...job
}) => job;

const findDispatchedRun = async (workflowUrl, dispatchRequestedAt) => {
  const branch = process.env.GITHUB_BRANCH || "main";
  const query = new URLSearchParams({
    event: "workflow_dispatch",
    branch,
    per_page: "20",
  });
  const { workflow_runs: runs } = await githubRequest(
    `${workflowUrl}/runs?${query.toString()}`,
  );
  const triggerTime = Date.parse(dispatchRequestedAt);
  // GitHub's created_at values are usually precise only to a whole second.
  const earliestPossibleRunTime = Math.floor(triggerTime / 1000) * 1000;

  return runs
    .filter(
      (run) =>
        run.event === "workflow_dispatch" &&
        run.head_branch === branch &&
        Date.parse(run.created_at) >= earliestPossibleRunTime,
    )
    .sort(
      (left, right) =>
        Math.abs(Date.parse(left.created_at) - triggerTime) -
        Math.abs(Date.parse(right.created_at) - triggerTime),
    )[0];
};

export const triggerIngest = async () => {
  const jobId = randomUUID();
  const job = {
    jobId,
    status: "running",
    startedAt: new Date().toISOString(),
    stdout: "",
    stderr: "",
  };
  jobs.set(jobId, job);

  let workflowUrl;
  try {
    ({ workflowUrl } = await workflowPath());
    job.workflowUrl = workflowUrl;
    job.dispatchRequestedAt = new Date().toISOString();
    await githubRequest(`${workflowUrl}/dispatches`, {
      method: "POST",
      headers: { "Content-Type": "application/vnd.github+json" },
      body: JSON.stringify({ ref: process.env.GITHUB_BRANCH || "main" }),
    });
  } catch (error) {
    job.status = "failed";
    job.error =
      error instanceof Error
        ? error.message
        : "Unknown GitHub Actions dispatch error.";
    job.finishedAt = new Date().toISOString();
  }

  if (job.status === "running") {
    try {
      const run = await findDispatchedRun(workflowUrl, job.dispatchRequestedAt);
      if (run) job.runId = run.id;
    } catch {
      // Dispatch succeeded. Run discovery can be retried when the client polls status.
    }
  }

  return publicJob(job);
};

export const getJobStatus = async (jobId) => {
  const job = jobs.get(jobId);
  if (!job) return undefined;
  if (job.status !== "running") return publicJob(job);

  if (!job.runId) {
    try {
      const run = await findDispatchedRun(
        job.workflowUrl,
        job.dispatchRequestedAt,
      );
      if (!run) return publicJob(job);
      job.runId = run.id;
    } catch {
      // Keep a successfully dispatched job running until GitHub exposes its run.
      return publicJob(job);
    }
  }

  const owner = encodeURIComponent(process.env.GITHUB_OWNER);
  const repository = encodeURIComponent(process.env.GITHUB_REPO);
  const run = await githubRequest(
    `/repos/${owner}/${repository}/actions/runs/${job.runId}`,
  );
  job.status =
    run.status === "completed"
      ? run.conclusion === "success"
        ? "completed"
        : "failed"
      : "running";

  if (job.status !== "running") {
    job.finishedAt = new Date().toISOString();
    if (job.status === "failed") {
      job.error = `GitHub Actions run completed with conclusion: ${run.conclusion || "unknown"}.`;
    }
  }

  return publicJob(job);
};
