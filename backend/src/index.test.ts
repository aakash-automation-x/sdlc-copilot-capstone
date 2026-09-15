import { describe, it, expect } from "vitest";
import { app } from "./index.js";

describe("backend scaffolding", () => {
  // NFR-001: skeleton must build and expose the Express app for later tasks.
  it("exports an Express app", () => {
    expect(typeof app).toBe("function");
  });
});
