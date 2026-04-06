/**
 * Media Normalizer
 *
 * Converts raw media artifacts (photos, videos, transcripts) into structured
 * candidates with car IDs, event dates, and confidence scores.
 *
 * Input: Media metadata (filename, EXIF, transcript text, file timestamps)
 * Output: Normalized candidate objects with provenance tracking
 */

const fs = require('fs');
const path = require('path');

/**
 * Car database - maps known cars to all their aliases
 * Loaded from oio-brain/cars/ structure at runtime
 */
class CarDatabase {
  constructor() {
    this.cars = new Map(); // carId -> { carId, names, driver, slug, ... }
    this.nameIndex = new Map(); // normalized_name -> [carId, ...]
  }

  /**
   * Load cars from brain structure
   * Expects structure: cars/{driver}/{car-slug}/Overview.md
   */
  loadFromBrain(brainsPath) {
    // For now, seed with known cars from current-state
    // Full implementation would parse Overview.md files
    const knownCars = [
      {
        carId: 'mr2-goblin',
        driver: 'ian',
        slug: 'mr2-goblin',
        names: ['Goblin', 'MR2', 'MR2 Goblin', '1985 Toyota MR2'],
        year: 1985,
        make: 'Toyota',
        model: 'MR2'
      },
      {
        carId: 'celica-dale',
        driver: 'ian',
        slug: 'celica-dale',
        names: ['Dale', 'Celica', '1972 Toyota Celica'],
        year: 1972,
        make: 'Toyota',
        model: 'Celica'
      },
      {
        carId: 'fit-fitty-cent',
        driver: 'ian',
        slug: 'fit-fitty-cent',
        names: ['Fitty Cent', 'Fit', 'GE8', 'Honda Fit', '2009 Honda Fit'],
        year: 2009,
        make: 'Honda',
        model: 'Fit'
      },
      {
        carId: 'cressida-nessie',
        driver: 'ian',
        slug: 'cressida-nessie',
        names: ['Nessie', 'Cressida', '1982 Toyota Cressida'],
        year: 1982,
        make: 'Toyota',
        model: 'Cressida'
      },
      {
        carId: 'corolla-killer',
        driver: 'ian',
        slug: 'corolla-killer',
        names: ['Killer Corolla', 'Corolla', '1977 Toyota Corolla'],
        year: 1977,
        make: 'Toyota',
        model: 'Corolla'
      },
      {
        carId: 'dauphine-geoffrey',
        driver: 'ian',
        slug: 'dauphine-geoffrey',
        names: ['Geoffrey', 'Dauphine', '1962 Renault Dauphine'],
        year: 1962,
        make: 'Renault',
        model: 'Dauphine'
      }
    ];

    for (const car of knownCars) {
      this.cars.set(car.carId, car);

      // Index all aliases
      for (const name of car.names) {
        const normalized = this._normalize(name);
        if (!this.nameIndex.has(normalized)) {
          this.nameIndex.set(normalized, []);
        }
        this.nameIndex.get(normalized).push(car.carId);
      }
    }
  }

  /**
   * Find car by any alias, return carId
   * Returns null if not found
   */
  findCarByName(text) {
    const normalized = this._normalize(text);
    const matches = this.nameIndex.get(normalized);
    return matches && matches.length > 0 ? matches[0] : null;
  }

  /**
   * Get car object by carId
   */
  getCar(carId) {
    return this.cars.get(carId);
  }

  _normalize(text) {
    return text.toLowerCase().trim();
  }
}

/**
 * Extract candidate car IDs from text
 *
 * Strategy:
 * 1. Match explicit mentions in transcript
 * 2. Find car nicknames and model names
 * 3. Return ordered list with confidence scores
 */
class CarIdExtractor {
  constructor(carDb) {
    this.carDb = carDb;
  }

  /**
   * Extract car candidates from transcript text
   * Returns: [{ carId, confidence, signals: [...] }, ...]
   */
  extractFromTranscript(transcriptText) {
    if (!transcriptText) return [];

    const candidates = new Map(); // carId -> { carId, confidence, signals }

    // Split into sentences and search for car mentions
    const sentences = transcriptText.match(/[^.!?]+[.!?]+/g) || [transcriptText];

    for (const sentence of sentences) {
      // Try to match each car in the database
      for (const [carId, car] of this.carDb.cars) {
        let highestConfidence = 0;

        // Check each name/alias
        for (const name of car.names) {
          // Case-insensitive regex search
          const pattern = new RegExp(`\\b${this._escapeRegex(name)}\\b`, 'i');
          if (pattern.test(sentence)) {
            // Confidence based on name specificity
            // Longer, more specific names = higher confidence
            const confidence = Math.min(1.0, 0.5 + (name.length / 50));
            highestConfidence = Math.max(highestConfidence, confidence);
          }
        }

        if (highestConfidence > 0) {
          if (!candidates.has(carId)) {
            candidates.set(carId, {
              carId,
              confidence: highestConfidence,
              signals: []
            });
          } else {
            // Already found this car; update confidence if higher
            const existing = candidates.get(carId);
            if (highestConfidence > existing.confidence) {
              existing.confidence = highestConfidence;
            }
          }
          candidates.get(carId).signals.push({ type: 'transcript_mention', sentence: sentence.trim() });
        }
      }
    }

    // Sort by confidence descending
    return Array.from(candidates.values()).sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Extract car candidates from filename
   * Returns: [{ carId, confidence, signals: [...] }, ...]
   */
  extractFromFilename(filename) {
    const candidates = new Map();

    for (const [carId, car] of this.carDb.cars) {
      for (const name of car.names) {
        const pattern = new RegExp(this._escapeRegex(name), 'i');
        if (pattern.test(filename)) {
          const confidence = Math.min(1.0, 0.6 + (name.length / 50));
          if (!candidates.has(carId)) {
            candidates.set(carId, {
              carId,
              confidence,
              signals: []
            });
          } else {
            candidates.get(carId).confidence = Math.max(candidates.get(carId).confidence, confidence);
          }
          candidates.get(carId).signals.push({ type: 'filename_match', pattern: name });
        }
      }
    }

    return Array.from(candidates.values()).sort((a, b) => b.confidence - a.confidence);
  }

  _escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

/**
 * Extract candidate event dates from media
 *
 * Strategy:
 * 1. Parse EXIF metadata (creation date)
 * 2. Use file modification time
 * 3. Extract dates from transcript timestamps and mentions
 * 4. Return ordered candidates with confidence
 */
class DateExtractor {
  /**
   * Extract date candidates from EXIF metadata
   */
  extractFromExif(exifData) {
    const candidates = [];

    if (exifData && exifData.DateTime) {
      try {
        const date = this._parseExifDate(exifData.DateTime);
        if (date) {
          candidates.push({
            date: date,
            confidence: 0.95,
            signals: [{ type: 'exif_datetime', raw: exifData.DateTime }]
          });
        }
      } catch (e) {
        // Skip malformed EXIF
      }
    }

    return candidates;
  }

  /**
   * Extract date from file modification time
   */
  extractFromFileTime(filePath) {
    try {
      const stats = fs.statSync(filePath);
      const date = new Date(stats.mtime);

      return {
        date: this._normalizeDate(date),
        confidence: 0.7,
        signals: [{ type: 'file_mtime', timestamp: stats.mtime.toISOString() }]
      };
    } catch (e) {
      return null;
    }
  }

  /**
   * Extract dates from transcript text
   * Looks for patterns like "March 22" or "2026-03-22" or "today"
   */
  extractFromTranscript(transcriptText, referenceDate = new Date()) {
    if (!transcriptText) return [];

    const candidates = [];
    const seenDates = new Set();

    // ISO date pattern: YYYY-MM-DD
    const isoPattern = /(\d{4})-(\d{2})-(\d{2})/g;
    let match;
    while ((match = isoPattern.exec(transcriptText)) !== null) {
      const date = `${match[1]}-${match[2]}-${match[3]}`;
      if (!seenDates.has(date)) {
        candidates.push({
          date,
          confidence: 0.95,
          signals: [{ type: 'transcript_iso_date', text: match[0] }]
        });
        seenDates.add(date);
      }
    }

    // Month + Day pattern: "March 22" or "Mar 22"
    const monthDayPattern = /(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})/gi;
    while ((match = monthDayPattern.exec(transcriptText)) !== null) {
      try {
        const dateStr = `${match[1]} ${match[2]} ${referenceDate.getFullYear()}`;
        const parsedDate = new Date(dateStr);
        if (!isNaN(parsedDate.getTime())) {
          const date = this._normalizeDate(parsedDate);
          if (!seenDates.has(date)) {
            candidates.push({
              date,
              confidence: 0.75,
              signals: [{ type: 'transcript_month_day', text: match[0] }]
            });
            seenDates.add(date);
          }
        }
      } catch (e) {
        // Skip malformed dates
      }
    }

    return candidates.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Normalize date to YYYY-MM-DD format
   */
  _normalizeDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  /**
   * Parse EXIF DateTime format: "YYYY:MM:DD HH:MM:SS"
   */
  _parseExifDate(exifDateTime) {
    const match = exifDateTime.match(/^(\d{4}):(\d{2}):(\d{2})/);
    if (!match) return null;
    return `${match[1]}-${match[2]}-${match[3]}`;
  }
}

/**
 * Main Normalizer class - orchestrates extraction
 */
class MediaNormalizer {
  constructor(brainsPath) {
    this.carDb = new CarDatabase();
    this.carDb.loadFromBrain(brainsPath);

    this.carExtractor = new CarIdExtractor(this.carDb);
    this.dateExtractor = new DateExtractor();
  }

  /**
   * Normalize a media artifact (photo, video, transcript)
   *
   * Input:
   *   mediaPath: full path to file
   *   transcriptText: optional transcript content
   *   exifData: optional EXIF metadata object
   *
   * Output: NormalizedCandidate
   *   {
   *     mediaPath,
   *     mediaType,
   *     carCandidates: [{ carId, confidence, signals }, ...],
   *     dateCandidates: [{ date, confidence, signals }, ...],
   *     topCarMatch: { carId, confidence } or null,
   *     topDateMatch: { date, confidence } or null,
   *     provenance: { ... }
   *   }
   */
  normalize(mediaPath, transcriptText = null, exifData = null) {
    const filename = path.basename(mediaPath);
    const mediaType = this._detectMediaType(filename);

    // Extract car candidates
    const carCandidates = this.carExtractor.extractFromFilename(filename);
    if (transcriptText) {
      const transcriptCars = this.carExtractor.extractFromTranscript(transcriptText);
      // Merge, preferring higher confidence
      carCandidates.push(...transcriptCars);
      carCandidates.sort((a, b) => b.confidence - a.confidence);
    }

    // Extract date candidates
    const dateCandidates = [];
    if (exifData) {
      dateCandidates.push(...this.dateExtractor.extractFromExif(exifData));
    }
    if (fs.existsSync(mediaPath)) {
      const fileDate = this.dateExtractor.extractFromFileTime(mediaPath);
      if (fileDate) dateCandidates.push(fileDate);
    }
    if (transcriptText) {
      dateCandidates.push(...this.dateExtractor.extractFromTranscript(transcriptText));
    }

    return {
      mediaPath,
      filename,
      mediaType,
      carCandidates,
      dateCandidates,
      topCarMatch: carCandidates.length > 0 ? {
        carId: carCandidates[0].carId,
        confidence: carCandidates[0].confidence
      } : null,
      topDateMatch: dateCandidates.length > 0 ? {
        date: dateCandidates[0].date,
        confidence: dateCandidates[0].confidence
      } : null,
      provenance: {
        extracted_at: new Date().toISOString(),
        sources: {
          filename: !!filename,
          transcript: !!transcriptText,
          exif: !!exifData,
          file_mtime: fs.existsSync(mediaPath)
        }
      }
    };
  }

  _detectMediaType(filename) {
    const ext = path.extname(filename).toLowerCase();
    if (['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext)) return 'photo';
    if (['.mp4', '.mov', '.avi', '.mkv'].includes(ext)) return 'video';
    if (['.txt', '.md'].includes(ext)) return 'transcript';
    return 'unknown';
  }
}

module.exports = {
  MediaNormalizer,
  CarDatabase,
  CarIdExtractor,
  DateExtractor
};
