import express from "express";

export const app = express();

// Liveness stub; full health probes arrive in TASK-020.
app.get("/healthz", (_req, res) => {
  res.json({ status: "ok" });
});

const port = Number(process.env.PORT ?? 3000);

// Only listen when run directly, so tests can import `app` without a live port.
if (process.env.NODE_ENV !== "test") {
  app.listen(port, () => {
    console.log(`auth api listening on ${port}`);
  });
}
