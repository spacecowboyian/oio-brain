# OIO Media Normalization Pipeline

**Status:** Proof-of-concept implemented for OUT-285

This directory contains the media normalization system that converts raw photos, videos, and transcripts into structured candidates with car IDs, event dates, and confidence scores.

## Vision

Part of the larger media-to-timeline linking system (OUT-278) that enables:

1. **Automatic media classification** — When you upload a photo or transcript, the normalizer extracts:
   - Which car(s) are featured
   - What date it's from
   - Confidence scores for each candidate

2. **Structured output for downstream processing** — The normalized candidates feed into:
   - Event-linking resolver (OUT-286) — matches to timeline events with fallback handling
   - Build log generation — creates Instagram posts + blog posts
   - Video script generation — assembles car story arcs from connected history

## What's Implemented

### `normalizer.js` (Main Module)

The core media normalization engine with four classes:

#### `CarDatabase`
- Loads known cars from the brain structure
- Maps nicknames → car IDs (case-insensitive)
- Enables robust car identification

**Known cars:**
- `mr2-goblin` — 1985 Toyota MR2
- `celica-dale` — 1972 Toyota Celica
- `fit-fitty-cent` — 2009 Honda Fit GE8
- `cressida-nessie` — 1982 Toyota Cressida
- `corolla-killer` — 1977 Toyota Corolla
- `dauphine-geoffrey` — 1962 Renault Dauphine

#### `CarIdExtractor`
Finds car candidates by:
- **Transcript matching** — Searches for car names/nicknames in transcript text
- **Filename matching** — Finds car references in filenames
- **Confidence scoring** — Longer, more specific names get higher confidence

Example:
```javascript
const extractor = new CarIdExtractor(carDb);
const candidates = extractor.extractFromTranscript(
  "I worked on the Goblin today..."
);
// Output: [{ carId: 'mr2-goblin', confidence: 0.75, signals: [...] }]
```

#### `DateExtractor`
Finds date candidates from:
- **EXIF metadata** — Photo creation timestamps (highest confidence, 0.95)
- **File modification time** — mtime fallback (0.7)
- **Transcript dates** — ISO dates like "2026-03-22" (0.95) and natural language like "March 22" (0.75)

Example:
```javascript
const extractor = new DateExtractor();
const dates = extractor.extractFromTranscript(
  "This was on March 22, 2026..."
);
// Output: [{ date: '2026-03-22', confidence: 0.75, signals: [...] }]
```

#### `MediaNormalizer`
Orchestrates the full normalization pipeline:

```javascript
const normalizer = new MediaNormalizer('/path/to/oio-brain');

const result = normalizer.normalize(
  mediaPath,           // '/path/to/photo.jpg'
  transcriptText,      // optional
  exifData             // optional
);

// Output: {
//   mediaPath, mediaType, filename,
//   carCandidates: [{ carId, confidence, signals }, ...],
//   dateCandidates: [{ date, confidence, signals }, ...],
//   topCarMatch: { carId, confidence },
//   topDateMatch: { date, confidence },
//   provenance: { extracted_at, sources }
// }
```

### `normalizer.test.js` (50 Unit Tests)

Comprehensive test coverage including:
- Car database lookups (exact, case-insensitive, multi-word)
- Transcript parsing (single cars, multiple cars, confidence ordering)
- Filename extraction (with/without case variations)
- Date extraction (EXIF, file timestamps, ISO dates, natural language)
- Integration tests (multi-source normalization, ambiguous cases)
- Edge cases (empty strings, partial word matching, multiple dates)

**Run tests:**
```bash
cd /Users/ian/repos/oio-brain
node pipeline/normalizer.test.js
```

**Result:** ✅ 50/50 tests passing

### `normalize-media.js` (CLI Tool)

Command-line interface for testing the normalizer:

```bash
# Simple photo
node pipeline/normalize-media.js photo.jpg

# With transcript
node pipeline/normalize-media.js video.mp4 --transcript transcript.txt

# With EXIF metadata
node pipeline/normalize-media.js photo.jpg --exif '{"DateTime":"2026:03:22 14:30:45"}'

# Output as JSON for scripting
OUTPUT_JSON=1 node pipeline/normalize-media.js photo.jpg > result.json
```

## Data Structures

### Normalized Candidate Output

```javascript
{
  mediaPath: "/path/to/IMG_20260322_goblin.jpg",
  filename: "IMG_20260322_goblin.jpg",
  mediaType: "photo",  // 'photo' | 'video' | 'transcript' | 'unknown'

  // All car candidates, ranked by confidence
  carCandidates: [
    {
      carId: "mr2-goblin",
      confidence: 0.85,  // 0.0 to 1.0
      signals: [
        { type: "filename_match", pattern: "Goblin" },
        { type: "transcript_mention", sentence: "The Goblin is running..." }
      ]
    }
  ],

  // All date candidates, ranked by confidence
  dateCandidates: [
    {
      date: "2026-03-22",  // YYYY-MM-DD format
      confidence: 0.95,    // 0.0 to 1.0
      signals: [
        { type: "exif_datetime", raw: "2026:03:22 14:30:45" }
      ]
    }
  ],

  // Single best match for each dimension
  topCarMatch: { carId: "mr2-goblin", confidence: 0.85 } || null,
  topDateMatch: { date: "2026-03-22", confidence: 0.95 } || null,

  // Traceability
  provenance: {
    extracted_at: "2026-04-05T17:40:00.000Z",
    sources: {
      filename: true,
      transcript: true,
      exif: false,
      file_mtime: true
    }
  }
}
```

## Confidence Scoring Model

### Car Matching

| Signal | Confidence |
|--------|-----------|
| Exact nickname in transcript | 0.65–0.75 |
| Model name (e.g., "MR2") | 0.50–0.60 |
| Multi-word nickname | 0.70–0.85 |
| Filename mention | 0.60–0.70 |

Formula: `base + (len / 50)` where len = name length

### Date Matching

| Source | Confidence |
|--------|-----------|
| EXIF DateTime | 0.95 |
| ISO date in transcript | 0.95 |
| Month + day in transcript | 0.75 |
| File modification time | 0.70 |

## Integration Points

### Input: Media + Metadata

- **Photos/videos:** File path, optional transcript, optional EXIF
- **Transcripts:** Raw text (extracted from Ian's daily notes or YouTube transcripts)
- **File timestamps:** Auto-extracted from filesystem

### Output: Candidates for Event Linking

The normalized candidates become the input to OUT-286 (event-linking resolver), which:
- Matches candidates to known car timeline events
- Handles conflicts and ambiguity with conservative defaults
- Maintains audit trail of decisions
- Exposes human override mechanism

## Implementation Notes

### Car Database Seeding

Currently hardcoded with known cars from `active/current-state.md`. Future enhancement:
```javascript
// Parse Overview.md files automatically
for (const driverFolder in cars/) {
  for (const carFolder in cars/{driver}/) {
    const carData = parseMarkdown(cars/{driver}/{car}/Overview.md);
    db.addCar(carData);
  }
}
```

### Transcript Sources

- **Intake dailies:** `intake/dailies/*.txt` — Raw daily notes from Ian
- **YouTube transcripts:** `transcripts/*.vtt` — Auto-fetched from YouTube API
- **Manual transcripts:** Any text content provided during processing

### Future Enhancements

1. **EXIF parsing library** — Use `exif-parser` npm package for robust photo metadata
2. **Transcript confidence** — Lower confidence for low-quality transcripts
3. **Temporal context** — Consider "today" / "yesterday" relative to known event dates
4. **Visual recognition** — Computer vision to detect cars in photos (future)
5. **Fuzzy matching** — Handle misspelled car names

## Files

| File | Purpose |
|------|---------|
| `normalizer.js` | Core normalizer implementation (4 classes) |
| `normalizer.test.js` | Comprehensive unit tests (50 tests) |
| `normalize-media.js` | CLI tool for testing |
| `README.md` | This file |

## Related Tasks

- **OUT-278** — "The dream" vision document (parent)
- **OUT-284** — (Dependency — unknown status)
- **OUT-285** — This task: Build media/transcript normalization pipeline ✅
- **OUT-286** — Implement event-linking resolver (downstream)

## Testing

```bash
# Run full test suite
node pipeline/normalizer.test.js

# Test with a real media file
node pipeline/normalize-media.js /path/to/photo.jpg

# Test with transcript
node pipeline/normalize-media.js /path/to/video.mp4 \
  --transcript /path/to/transcript.txt

# Test with EXIF metadata
node pipeline/normalize-media.js photo.jpg \
  --exif '{"DateTime":"2026:03:22 14:30:45"}'

# Export JSON for processing
OUTPUT_JSON=1 node pipeline/normalize-media.js photo.jpg > result.json
```

## Status

✅ **OUT-285 Acceptance Criteria Met:**

- [x] Normalizer outputs deterministic candidate objects
  - Seeded with known cars from OIO
  - Confidence model defined and tested
  - Fallback behavior documented (empty results if no matches)

- [x] Confidence model + fallback behavior documented
  - Car matching: transcript mention, filename match, model name
  - Date matching: EXIF, ISO date, month/day pattern, file mtime
  - Fallback: Empty candidate lists if no matches found
  - Provenance tracked for all signals

- [x] Unit tests cover ambiguous multi-car updates
  - Test: Multiple cars in transcript (Goblin + Fit)
  - Test: Same car mentioned multiple ways
  - Test: Filename + transcript candidates merged
  - Test: Date extraction from multiple sources
  - 50 tests total, 100% passing

---

**Next:** Integrate with OUT-286 (event-linking resolver)
