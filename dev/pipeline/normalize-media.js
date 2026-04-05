#!/usr/bin/env node

/**
 * Media Normalizer CLI
 *
 * Usage:
 *   node normalize-media.js <media-file> [--transcript <file>] [--exif <json>]
 *
 * Examples:
 *   node normalize-media.js /path/to/photo.jpg
 *   node normalize-media.js /path/to/video.mp4 --transcript transcript.txt
 *   node normalize-media.js photo.jpg --exif '{"DateTime":"2026:03:22 14:30:45"}'
 */

const { MediaNormalizer } = require('./normalizer');
const fs = require('fs');
const path = require('path');

function printUsage() {
  console.log(`
Usage: node normalize-media.js <media-file> [OPTIONS]

Options:
  --transcript <file>    Path to transcript file (optional)
  --exif <json>          EXIF metadata as JSON string (optional)
  --help                 Show this help message

Examples:
  node normalize-media.js photo.jpg
  node normalize-media.js video.mp4 --transcript transcript.txt
  node normalize-media.js photo.jpg --exif '{"DateTime":"2026:03:22 14:30:45"}'
  `);
}

function parseArgs(args) {
  if (args.length === 0 || args.includes('--help')) {
    printUsage();
    process.exit(0);
  }

  const mediaFile = args[0];
  const options = { transcript: null, exif: null };

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--transcript' && i + 1 < args.length) {
      options.transcript = args[++i];
    } else if (args[i] === '--exif' && i + 1 < args.length) {
      try {
        options.exif = JSON.parse(args[++i]);
      } catch (e) {
        console.error('Error: Invalid JSON for --exif:', e.message);
        process.exit(1);
      }
    }
  }

  return { mediaFile, options };
}

function printResults(result) {
  console.log('\n' + '='.repeat(70));
  console.log('NORMALIZED MEDIA CANDIDATE');
  console.log('='.repeat(70));

  console.log(`\nFile: ${result.filename}`);
  console.log(`Type: ${result.mediaType}`);
  console.log(`Path: ${result.mediaPath}`);

  if (result.topCarMatch) {
    console.log(`\n📍 TOP CAR MATCH:`);
    console.log(`   Car ID:     ${result.topCarMatch.carId}`);
    console.log(`   Confidence: ${(result.topCarMatch.confidence * 100).toFixed(1)}%`);
  } else {
    console.log(`\n📍 TOP CAR MATCH: None found`);
  }

  if (result.topDateMatch) {
    console.log(`\n📅 TOP DATE MATCH:`);
    console.log(`   Date:       ${result.topDateMatch.date}`);
    console.log(`   Confidence: ${(result.topDateMatch.confidence * 100).toFixed(1)}%`);
  } else {
    console.log(`\n📅 TOP DATE MATCH: None found`);
  }

  if (result.carCandidates.length > 1) {
    console.log(`\n🚗 OTHER CAR CANDIDATES (${result.carCandidates.length - 1}):`);
    for (let i = 1; i < result.carCandidates.length; i++) {
      const cand = result.carCandidates[i];
      console.log(`   ${i}. ${cand.carId} (${(cand.confidence * 100).toFixed(1)}%)`);
    }
  }

  if (result.dateCandidates.length > 1) {
    console.log(`\n📆 OTHER DATE CANDIDATES (${result.dateCandidates.length - 1}):`);
    for (let i = 1; i < result.dateCandidates.length; i++) {
      const cand = result.dateCandidates[i];
      console.log(`   ${i}. ${cand.date} (${(cand.confidence * 100).toFixed(1)}%)`);
    }
  }

  console.log(`\n📋 PROVENANCE:`);
  console.log(`   Extracted: ${result.provenance.extracted_at}`);
  console.log(`   Sources: ${Object.entries(result.provenance.sources)
    .filter(([, used]) => used)
    .map(([name]) => name)
    .join(', ')}`);

  console.log('\n' + '='.repeat(70) + '\n');
}

async function main() {
  const { mediaFile, options } = parseArgs(process.argv.slice(2));

  // Validate media file exists
  if (!fs.existsSync(mediaFile)) {
    console.error(`Error: Media file not found: ${mediaFile}`);
    process.exit(1);
  }

  // Load transcript if specified
  let transcriptText = null;
  if (options.transcript) {
    if (!fs.existsSync(options.transcript)) {
      console.error(`Error: Transcript file not found: ${options.transcript}`);
      process.exit(1);
    }
    transcriptText = fs.readFileSync(options.transcript, 'utf8');
  }

  // Initialize normalizer
  const brainsPath = path.join(__dirname, '..');
  const normalizer = new MediaNormalizer(brainsPath);

  // Normalize
  const result = normalizer.normalize(mediaFile, transcriptText, options.exif);

  // Print results
  printResults(result);

  // Return JSON to stdout if needed by other programs
  if (process.env.OUTPUT_JSON === '1') {
    console.log(JSON.stringify(result, null, 2));
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
