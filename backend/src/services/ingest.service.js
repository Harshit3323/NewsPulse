import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const serviceDirectory = path.dirname(fileURLToPath(import.meta.url));
const backendDirectory = path.resolve(serviceDirectory, "../..");
const projectDirectory = path.resolve(backendDirectory, "..");
const jobs = new Map();
const maxLogLength = 4000;

const localPythonExecutable = path.join(
  projectDirectory,
  "scraper",
  ".venv",
  "Scripts",
  "python.exe",
);
const pythonExecutable =
  process.env.PYTHON_EXECUTABLE ||
  (existsSync(localPythonExecutable) ? localPythonExecutable : "python");

export const startIngestJob = () => {
  const jobId = randomUUID();
  const job = {
    jobId,
    status: "running",
    startedAt: new Date().toISOString(),
    stdout: "",
    stderr: "",
  };
  jobs.set(jobId, job);

  const child = spawn(pythonExecutable, ["-m", "scraper.run"], {
    cwd: projectDirectory,
    env: process.env,
    windowsHide: true,
  });

  const captureOutput = (stream, chunk) => {
    job[stream] = `${job[stream]}${chunk.toString()}`.slice(-maxLogLength);
  };

  child.stdout.on("data", (chunk) => captureOutput("stdout", chunk));
  child.stderr.on("data", (chunk) => captureOutput("stderr", chunk));

  child.on("error", (error) => {
    jobs.set(jobId, {
      ...job,
      status: "failed",
      error: error.message,
      finishedAt: new Date().toISOString(),
    });
  });

  child.on("close", (exitCode) => {
    if (jobs.get(jobId)?.status === "failed") return;

    jobs.set(jobId, {
      ...job,
      status: exitCode === 0 ? "completed" : "failed",
      exitCode,
      finishedAt: new Date().toISOString(),
    });
  });

  return job;
};

export const getIngestJob = (jobId) => jobs.get(jobId);
