import pg from "pg";

let pool: pg.Pool | undefined;

export function getPool(): pg.Pool {
  if (!pool) {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL is not set"); // fail closed on misconfig
    }
    pool = new pg.Pool({ connectionString });
  }
  return pool;
}
