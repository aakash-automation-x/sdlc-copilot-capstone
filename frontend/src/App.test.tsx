import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { App } from "./App.js";

describe("App scaffolding", () => {
  // NFR-001: skeleton renders so the login UI (TASK-015) can build on it.
  it("renders the app shell", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: /ecommerce login/i }),
    ).toBeInTheDocument();
  });
});
