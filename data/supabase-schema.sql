-- OIO Racing - Supabase Schema
-- Google Photos → Social Post workflow
--
-- Run this once in the Supabase SQL editor to create the required tables.
-- Project: https://zdjughkxryhabduhsdgg.supabase.co

-- -----------------------------------------------------------------------
-- photos
-- Central record for every photo ingested from the Google Photos album.
-- Tracks the full lifecycle from ingest through posting.
-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS photos (
  id                          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Source identifiers
  source_photo_id             TEXT        UNIQUE NOT NULL,  -- Google Photos media item ID
  source_album_id             TEXT,                         -- Google Photos album ID

  -- Asset URLs (stored in Supabase)
  image_url                   TEXT,                         -- Full-res URL in oio-photos bucket
  thumbnail_url               TEXT,                         -- Thumbnail URL (Google-sized or generated)

  -- Timestamps
  captured_at                 TIMESTAMPTZ,                  -- Original capture time from EXIF/Google
  ingested_at                 TIMESTAMPTZ DEFAULT NOW(),    -- When first written to Supabase

  -- Caption data
  source_description          TEXT,                         -- Original description from Google Photos
  rough_caption               TEXT,                         -- Human-entered or auto-pulled rough caption
  final_caption               TEXT,                         -- AI-generated polished caption

  -- Vehicle / category assignment
  vehicle_key                 TEXT,                         -- Canonical vehicle key (human-set or confirmed)
  category                    TEXT,                         -- e.g. 'vehicle', 'team', 'event', 'other'
  auto_identified_vehicle_key TEXT,                         -- AI-guessed vehicle key
  identification_confidence   FLOAT,                        -- 0.0–1.0 from Claude Vision

  -- Triage flags
  needs_triage                BOOLEAN     DEFAULT FALSE,    -- True when human review is required
  needs_vehicle_assignment    BOOLEAN     DEFAULT FALSE,
  needs_rough_caption         BOOLEAN     DEFAULT FALSE,

  -- Downstream status
  caption_status              TEXT        DEFAULT 'pending', -- pending | ready | generated | approved
  draft_status                TEXT        DEFAULT 'pending', -- pending | created | approved | posted
  postbridge_draft_id         TEXT,                          -- PostBridge post ID
  tentative_publish_at        TIMESTAMPTZ,                   -- Proposed publish date
  approved_for_posting        BOOLEAN     DEFAULT FALSE,
  posted_at                   TIMESTAMPTZ,

  -- Overall workflow state machine
  -- Values: ingested | auto_identified | needs_triage | metadata_complete
  --         | caption_generated | draft_created | approved | posted
  workflow_status             TEXT        DEFAULT 'ingested' NOT NULL,

  -- Audit
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at on any change
CREATE OR REPLACE FUNCTION update_photos_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS photos_updated_at ON photos;
CREATE TRIGGER photos_updated_at
  BEFORE UPDATE ON photos
  FOR EACH ROW EXECUTE PROCEDURE update_photos_updated_at();

-- Indexes
CREATE INDEX IF NOT EXISTS photos_workflow_status_idx  ON photos (workflow_status);
CREATE INDEX IF NOT EXISTS photos_vehicle_key_idx      ON photos (vehicle_key);
CREATE INDEX IF NOT EXISTS photos_needs_triage_idx     ON photos (needs_triage);
CREATE INDEX IF NOT EXISTS photos_ingested_at_idx      ON photos (ingested_at DESC);

-- -----------------------------------------------------------------------
-- caption_history
-- Preserves every generated caption so we can tune the model over time.
-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS caption_history (
  id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  photo_id    UUID        REFERENCES photos (id) ON DELETE CASCADE,
  caption     TEXT        NOT NULL,
  model       TEXT,                         -- claude model used
  prompt_hash TEXT,                         -- hash of the prompt for dedup
  approved    BOOLEAN     DEFAULT FALSE,    -- true when Ian selected/used this caption
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS caption_history_photo_id_idx ON caption_history (photo_id);

-- -----------------------------------------------------------------------
-- photo_processing_runs
-- One row per GitHub Actions run of the ingestion workflow.
-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS photo_processing_runs (
  id             UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  run_id         TEXT,                        -- GitHub Actions run ID
  started_at     TIMESTAMPTZ DEFAULT NOW(),
  finished_at    TIMESTAMPTZ,
  photos_seen    INT         DEFAULT 0,
  photos_new     INT         DEFAULT 0,
  photos_updated INT         DEFAULT 0,
  photos_skipped INT         DEFAULT 0,
  errors         JSONB,
  status         TEXT        DEFAULT 'running'  -- running | success | partial | failed
);
