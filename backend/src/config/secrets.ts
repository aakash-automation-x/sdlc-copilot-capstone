export interface SecretsProvider {
  getSecret(name: string): string | undefined;
  requireSecret(name: string): string;
}

export class EnvSecretsProvider implements SecretsProvider {
  getSecret(name: string): string | undefined {
    return process.env[name];
  }

  requireSecret(name: string): string {
    const value = process.env[name];
    if (!value) {
      throw new Error(`Missing required secret: ${name}`); // NFR-008: fail closed
    }
    return value;
  }
}
