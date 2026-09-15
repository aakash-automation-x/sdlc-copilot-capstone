import { SecretsProvider } from "./secrets.js";

export interface SigningKey {
  kid: string;
  secret: string;
}

export class SigningKeyRegistry {
  private readonly keys: Map<string, string>;
  private activeKid: string;

  constructor(keys: SigningKey[], activeKid: string) {
    if (keys.length === 0) {
      throw new Error("At least one signing key is required");
    }
    this.keys = new Map(keys.map((key) => [key.kid, key.secret]));
    if (!this.keys.has(activeKid)) {
      throw new Error(`Active kid not found: ${activeKid}`);
    }
    this.activeKid = activeKid;
  }

  getActiveKey(): SigningKey {
    // Non-null: the active kid is validated on construction and on rotate.
    return { kid: this.activeKid, secret: this.keys.get(this.activeKid)! };
  }

  // Old kids remain valid for verification during rotation.
  getVerificationSecret(kid: string): string | undefined {
    return this.keys.get(kid);
  }

  rotate(newActiveKid: string): void {
    if (!this.keys.has(newActiveKid)) {
      throw new Error(`Cannot rotate to unknown kid: ${newActiveKid}`);
    }
    this.activeKid = newActiveKid;
  }
}

export function loadSigningKeyRegistry(
  secrets: SecretsProvider,
): SigningKeyRegistry {
  const keys = JSON.parse(
    secrets.requireSecret("JWT_SIGNING_KEYS"),
  ) as SigningKey[];
  return new SigningKeyRegistry(keys, secrets.requireSecret("JWT_ACTIVE_KID"));
}
