import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { EnvSecretsProvider } from "./secrets.js";

describe("EnvSecretsProvider", () => {
  const key = "TEST_SECRET_VALUE";
  let original: string | undefined;

  beforeEach(() => {
    original = process.env[key];
    delete process.env[key];
  });

  afterEach(() => {
    if (original === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = original;
    }
  });

  it("returns the value from the environment", () => {
    // NFR-008: secrets come from the environment, never hard-coded.
    process.env[key] = "from-env";
    expect(new EnvSecretsProvider().getSecret(key)).toBe("from-env");
  });

  it("returns undefined for a missing optional secret", () => {
    expect(new EnvSecretsProvider().getSecret(key)).toBeUndefined();
  });

  it("throws for a missing required secret (fail closed)", () => {
    // NFR-008: fail closed on security-relevant misconfiguration.
    expect(() => new EnvSecretsProvider().requireSecret(key)).toThrow(
      /Missing required secret/,
    );
  });
});
