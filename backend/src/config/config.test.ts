import { describe, it, expect } from "vitest";
import { loadConfig } from "./index.js";
import type { SecretsProvider } from "./secrets.js";

function providerWith(values: Record<string, string>): SecretsProvider {
  return {
    getSecret: (name) => values[name],
    requireSecret: (name) => {
      const value = values[name];
      if (!value) {
        throw new Error(`Missing required secret: ${name}`);
      }
      return value;
    },
  };
}

describe("loadConfig", () => {
  it("reads database and redis connection strings via the provider", () => {
    // NFR-008: connection strings (with credentials) come from the provider.
    const config = loadConfig(
      providerWith({
        DATABASE_URL: "postgres://localhost/db",
        REDIS_URL: "redis://localhost:6379",
      }),
    );
    expect(config.databaseUrl).toBe("postgres://localhost/db");
    expect(config.redisUrl).toBe("redis://localhost:6379");
  });

  it("fails closed when a required secret is missing", () => {
    // NFR-008: misconfiguration must not silently start the service.
    expect(() =>
      loadConfig(providerWith({ REDIS_URL: "redis://localhost:6379" })),
    ).toThrow(/DATABASE_URL/);
  });
});
