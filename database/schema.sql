-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE "users" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "username" TEXT UNIQUE NOT NULL,
    "created_at" TIMESTAMPTZ DEFAULT now()
);

-- Neuro_events table
CREATE TABLE "neuro_events" (
    "id" UUID PRIMARY KEY,
    "user_id" UUID REFERENCES users(id),
    "source_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    "event_timestamp" TIMESTAMPTZ NOT NULL,
    "received_at" TIMESTAMPTZ DEFAULT now(),
    "metadata" JSONB,
    "mnemonic_signature" TEXT,
    "sentience_hash" BYTEA -- Storing vector as BYTEA, to be casted in the application
);

-- Indexes for neuro_events
CREATE INDEX ON neuro_events (user_id, event_timestamp DESC);
CREATE INDEX ON neuro_events USING gin(metadata);

-- Data_streams table
CREATE TABLE "data_streams" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "event_id" UUID REFERENCES neuro_events(id) ON DELETE CASCADE,
    "stream_type" TEXT NOT NULL,
    "storage_uri" TEXT NOT NULL,
    "metadata" JSONB
);

-- Memory_shards table
CREATE TABLE "memory_shards" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "event_id" UUID REFERENCES neuro_events(id) ON DELETE CASCADE,
    "cpu_source" TEXT NOT NULL,
    "shard_type" TEXT NOT NULL,
    "data" JSONB,
    "created_at" TIMESTAMPTZ DEFAULT now()
);

-- Indexes for memory_shards
CREATE INDEX ON memory_shards (event_id);
CREATE INDEX ON memory_shards USING gin(data);
