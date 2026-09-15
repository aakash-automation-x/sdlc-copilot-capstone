/* eslint-disable camelcase */
exports.shorthands = undefined;

exports.up = (pgm) => {
  pgm.createExtension("citext", { ifNotExists: true });

  pgm.createTable("users", {
    id: {
      type: "uuid",
      primaryKey: true,
      default: pgm.func("gen_random_uuid()"),
    },
    email: { type: "citext", unique: true },
    mobile: { type: "text", unique: true },
    password_hash: { type: "text", notNull: true }, // NFR-004: hash only
    created_at: {
      type: "timestamptz",
      notNull: true,
      default: pgm.func("now()"),
    },
  });
  // FR-014: an account must be reachable by at least one identifier.
  pgm.addConstraint("users", "users_identifier_present", {
    check: "email IS NOT NULL OR mobile IS NOT NULL",
  });

  pgm.createTable("refresh_tokens", {
    id: {
      type: "uuid",
      primaryKey: true,
      default: pgm.func("gen_random_uuid()"),
    },
    user_id: {
      type: "uuid",
      notNull: true,
      references: "users",
      onDelete: "CASCADE",
    },
    family_id: { type: "uuid", notNull: true }, // DD-5 reuse detection
    token_hash: { type: "text", notNull: true }, // NFR-007: never store raw
    remember_me: { type: "boolean", notNull: true, default: false }, // DD-3
    expires_at: { type: "timestamptz", notNull: true },
    revoked: { type: "boolean", notNull: true, default: false },
    created_at: {
      type: "timestamptz",
      notNull: true,
      default: pgm.func("now()"),
    },
  });
  pgm.createIndex("refresh_tokens", "user_id");
  pgm.createIndex("refresh_tokens", "family_id");

  pgm.createTable("audit_log", {
    id: {
      type: "uuid",
      primaryKey: true,
      default: pgm.func("gen_random_uuid()"),
    },
    user_id: { type: "uuid", references: "users", onDelete: "SET NULL" },
    identifier_ref: { type: "text" }, // NFR-009: masked
    source_ip: { type: "inet" },
    outcome: {
      type: "text",
      notNull: true,
      check: "outcome IN ('success','invalid','locked')",
    },
    created_at: {
      type: "timestamptz",
      notNull: true,
      default: pgm.func("now()"),
    },
  });
  pgm.createIndex("audit_log", "created_at");

  pgm.createTable("attempt_fallback", {
    // DD-2: only used on the Redis-down fail-open path.
    key: { type: "text", primaryKey: true },
    attempts: { type: "integer", notNull: true, default: 0 },
    expires_at: { type: "timestamptz", notNull: true },
  });
};

exports.down = (pgm) => {
  pgm.dropTable("attempt_fallback");
  pgm.dropTable("audit_log");
  pgm.dropTable("refresh_tokens");
  pgm.dropTable("users");
  pgm.dropExtension("citext", { ifExists: true });
};
