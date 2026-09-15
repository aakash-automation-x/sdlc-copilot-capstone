import { describe, it, expect } from "vitest";
import {
  SigningKeyRegistry,
  loadSigningKeyRegistry,
  type SigningKey,
} from "./signingKeys.js";
import type { SecretsProvider } from "./secrets.js";

const keys: SigningKey[] = [
  { kid: "k1", secret: "secret-one" },
  { kid: "k2", secret: "secret-two" },
];

describe("SigningKeyRegistry", () => {
  it("rejects an empty key set", () => {
    // DR-008: signing requires at least one key.
    expect(() => new SigningKeyRegistry([], "k1")).toThrow(
      /at least one signing key/i,
    );
  });

  it("rejects an active kid that does not exist", () => {
    expect(() => new SigningKeyRegistry(keys, "missing")).toThrow(
      /Active kid not found/,
    );
  });

  it("returns the active key for signing", () => {
    const registry = new SigningKeyRegistry(keys, "k1");
    expect(registry.getActiveKey()).toEqual({ kid: "k1", secret: "secret-one" });
  });

  it("verifies tokens signed with any known kid", () => {
    // DR-008: old kids stay valid for verification during rotation.
    const registry = new SigningKeyRegistry(keys, "k1");
    expect(registry.getVerificationSecret("k2")).toBe("secret-two");
    expect(registry.getVerificationSecret("unknown")).toBeUndefined();
  });

  it("rotates the active kid", () => {
    const registry = new SigningKeyRegistry(keys, "k1");
    registry.rotate("k2");
    expect(registry.getActiveKey().kid).toBe("k2");
  });

  it("refuses to rotate to an unknown kid", () => {
    const registry = new SigningKeyRegistry(keys, "k1");
    expect(() => registry.rotate("nope")).toThrow(/unknown kid/);
  });
});

describe("loadSigningKeyRegistry", () => {
  it("builds a registry from the secrets provider", () => {
    // NFR-008: key material is provided at runtime, not committed.
    const secrets: SecretsProvider = {
      getSecret: () => undefined,
      requireSecret: (name) =>
        name === "JWT_SIGNING_KEYS" ? JSON.stringify(keys) : "k2",
    };
    const registry = loadSigningKeyRegistry(secrets);
    expect(registry.getActiveKey().kid).toBe("k2");
  });
});
