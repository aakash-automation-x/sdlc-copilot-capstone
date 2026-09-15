import { SecretsProvider } from "./secrets.js";

export interface AppConfig {
  port: number;
  nodeEnv: string;
  databaseUrl: string;
  redisUrl: string;
}

export function loadConfig(secrets: SecretsProvider): AppConfig {
  return {
    port: Number(process.env.PORT ?? 3000),
    nodeEnv: process.env.NODE_ENV ?? "development",
    databaseUrl: secrets.requireSecret("DATABASE_URL"),
    redisUrl: secrets.requireSecret("REDIS_URL"),
  };
}
