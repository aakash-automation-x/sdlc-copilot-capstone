import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const migration = readFileSync(
  fileURLToPath(
    new URL(
      "../../migrations/1700000000000_initial-schema.cjs",
      import.meta.url,
    ),
  ),
  "utf8",
);

describe("initial schema migration", () => {
  it("creates the core tables", () => {
    // FR-014, FR-016
    for (const table of [
      "users",
      "refresh_tokens",
      "audit_log",
      "attempt_fallback",
    ]) {
      expect(migration).toContain(`createTable("${table}"`);
    }
  });

  it("stores only a password hash, never plaintext", () => {
    // NFR-004
    expect(migration).toContain("password_hash");
    expect(migration).not.toMatch(/password:\s*\{/);
  });

  it("supports refresh-token families for reuse detection", () => {
    // DD-5, NFR-007
    expect(migration).toContain("family_id");
  });

  it("constrains audit outcomes to known values", () => {
    // FR-016
    expect(migration).toContain("outcome IN ('success','invalid','locked')");
  });
});
