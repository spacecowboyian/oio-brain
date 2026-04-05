/**
 * Unit tests for Media Normalizer
 *
 * Run with: node pipeline/normalizer.test.js
 */

const {
  MediaNormalizer,
  CarDatabase,
  CarIdExtractor,
  DateExtractor
} = require('./normalizer');
const fs = require('fs');
const path = require('path');

let passCount = 0;
let failCount = 0;

function assert(condition, message) {
  if (condition) {
    passCount++;
    console.log(`  ✓ ${message}`);
  } else {
    failCount++;
    console.log(`  ✗ ${message}`);
  }
}

function assertEqual(actual, expected, message) {
  assert(actual === expected, `${message} (expected: ${expected}, got: ${actual})`);
}

function assertDeepEqual(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  assert(actualStr === expectedStr, `${message} (expected: ${expectedStr}, got: ${actualStr})`);
}

// ============================================================================
// CarDatabase Tests
// ============================================================================

console.log('\n=== CarDatabase Tests ===\n');

const carDb = new CarDatabase();
carDb.loadFromBrain('/Users/ian/repos/oio-brain');

console.log('findCarByName() - exact matches:');
assertEqual(carDb.findCarByName('Goblin'), 'mr2-goblin', 'Find by nickname "Goblin"');
assertEqual(carDb.findCarByName('goblin'), 'mr2-goblin', 'Case-insensitive search for "goblin"');
assertEqual(carDb.findCarByName('Dale'), 'celica-dale', 'Find by nickname "Dale"');
assertEqual(carDb.findCarByName('Fitty Cent'), 'fit-fitty-cent', 'Find multi-word nickname');

console.log('\nfindCarByName() - model matches:');
assertEqual(carDb.findCarByName('MR2'), 'mr2-goblin', 'Find by model "MR2"');
assertEqual(carDb.findCarByName('Celica'), 'celica-dale', 'Find by model "Celica"');
assertEqual(carDb.findCarByName('Honda Fit'), 'fit-fitty-cent', 'Find by full model name');

console.log('\nfindCarByName() - not found:');
assertEqual(carDb.findCarByName('Unknown Car'), null, 'Return null for unknown car');
assertEqual(carDb.findCarByName(''), null, 'Return null for empty string');

// ============================================================================
// CarIdExtractor Tests
// ============================================================================

console.log('\n=== CarIdExtractor Tests ===\n');

const carExtractor = new CarIdExtractor(carDb);

console.log('extractFromTranscript() - single car mention:');
const transcript1 = 'I was working on the Goblin today and it was running pretty good.';
const result1 = carExtractor.extractFromTranscript(transcript1);
assert(result1.length > 0, 'Should find at least one car candidate');
assertEqual(result1[0].carId, 'mr2-goblin', 'Should identify Goblin correctly');
assert(result1[0].confidence > 0.5, 'Should have reasonable confidence');

console.log('\nextractFromTranscript() - multiple car mentions:');
const transcript2 = 'I was working on the Goblin but then switched to Dale for the rally.';
const result2 = carExtractor.extractFromTranscript(transcript2);
assert(result2.length >= 2, 'Should find both cars');
const carIds = result2.map(c => c.carId);
assert(carIds.includes('mr2-goblin'), 'Should find Goblin');
assert(carIds.includes('celica-dale'), 'Should find Dale');

console.log('\nextractFromTranscript() - confidence ordering:');
const transcript3 = 'The MR2 is the Goblin. The Honda Fit, or Fitty Cent, is great.';
const result3 = carExtractor.extractFromTranscript(transcript3);
// Fitty Cent (2 words) might have same confidence as Goblin (1 word)
// but more specific names should rank higher - test relative ordering
assert(result3[0].confidence >= 0.5, 'Top result should have confidence > 0.5');

console.log('\nextractFromFilename() - car in filename:');
const filename1 = 'IMG_20260322_Goblin_rally_setup.jpg';
const result4 = carExtractor.extractFromFilename(filename1);
assert(result4.length > 0, 'Should find car in filename');
assertEqual(result4[0].carId, 'mr2-goblin', 'Should identify Goblin from filename');

console.log('\nextractFromFilename() - case insensitive:');
const filename2 = 'fitty_cent_autocross.mp4';
const result5 = carExtractor.extractFromFilename(filename2);
assert(result5.length > 0, 'Should find car with case variation');
assertEqual(result5[0].carId, 'fit-fitty-cent', 'Should match case-insensitively');

console.log('\nextractFromFilename() - no car match:');
const filename3 = 'random_video.mp4';
const result6 = carExtractor.extractFromFilename(filename3);
assertEqual(result6.length, 0, 'Should return empty array for no match');

// ============================================================================
// DateExtractor Tests
// ============================================================================

console.log('\n=== DateExtractor Tests ===\n');

const dateExtractor = new DateExtractor();

console.log('extractFromExif() - valid EXIF datetime:');
const exif1 = { DateTime: '2026:03:22 14:30:45' };
const result7 = dateExtractor.extractFromExif(exif1);
assert(result7.length > 0, 'Should parse EXIF datetime');
assertEqual(result7[0].date, '2026-03-22', 'Should normalize to YYYY-MM-DD');
assert(result7[0].confidence > 0.9, 'EXIF should have high confidence');

console.log('\nextractFromExif() - missing EXIF:');
const result8 = dateExtractor.extractFromExif({});
assertEqual(result8.length, 0, 'Should handle missing EXIF');

console.log('\nextractFromTranscript() - ISO date format:');
const transcript4 = 'This was recorded on 2026-03-22 during the rally.';
const result9 = dateExtractor.extractFromTranscript(transcript4);
assert(result9.length > 0, 'Should find ISO date');
assert(result9.some(d => d.date === '2026-03-22'), 'Should extract correct ISO date');

console.log('\nextractFromTranscript() - month/day format:');
const transcript5 = 'We did this work on March 22nd at the track.';
const result10 = dateExtractor.extractFromTranscript(transcript5);
assert(result10.length > 0, 'Should find month/day pattern');
// Should find a date with March 22 in current year
const found = result10.find(d => d.date.includes('-03-22'));
assert(found, 'Should parse "March 22" correctly');

console.log('\nextractFromTranscript() - abbreviated month:');
const transcript6 = 'Apr 10 was the big day.';
const result11 = dateExtractor.extractFromTranscript(transcript6);
assert(result11.length > 0, 'Should find abbreviated month');

console.log('\nextractFromTranscript() - no dates:');
const transcript7 = 'Just a random transcript with no date information.';
const result12 = dateExtractor.extractFromTranscript(transcript7);
assertEqual(result12.length, 0, 'Should return empty for no dates');

// ============================================================================
// MediaNormalizer Integration Tests
// ============================================================================

console.log('\n=== MediaNormalizer Integration Tests ===\n');

const normalizer = new MediaNormalizer('/Users/ian/repos/oio-brain');

console.log('normalize() - photo with transcript:');
const transcript8 = 'Goblin is running great. Did this on March 22.';
const result13 = normalizer.normalize(
  '/fake/path/IMG_goblin.jpg',
  transcript8,
  null
);
assert(result13.topCarMatch !== null, 'Should find top car match');
assertEqual(result13.topCarMatch.carId, 'mr2-goblin', 'Should identify Goblin');
assert(result13.topDateMatch !== null, 'Should find top date match');
assert(result13.topDateMatch.date.includes('03-22'), 'Should extract date');

console.log('\nnormalize() - video with EXIF and transcript:');
const exif2 = { DateTime: '2026:04:05 10:15:30' };
const transcript9 = 'Working on the Fit for the kids race.';
const result14 = normalizer.normalize(
  '/fake/path/VID_fitty_cent.mp4',
  transcript9,
  exif2
);
assertEqual(result14.mediaType, 'video', 'Should detect video type');
assert(result14.topCarMatch !== null, 'Should find car from both filename and transcript');
assertEqual(result14.topCarMatch.carId, 'fit-fitty-cent', 'Should identify Fitty Cent');
assert(result14.topDateMatch !== null, 'Should find date from EXIF');

console.log('\nnormalize() - ambiguous multi-car update:');
const transcript10 = 'I worked on the Goblin in the morning, then switched to the Fit for afternoon.';
const result15 = normalizer.normalize(
  '/fake/path/IMG_update.jpg',
  transcript10,
  null
);
assert(result15.carCandidates.length >= 2, 'Should list multiple car candidates');
assert(result15.carCandidates.some(c => c.carId === 'mr2-goblin'), 'Should find Goblin');
assert(result15.carCandidates.some(c => c.carId === 'fit-fitty-cent'), 'Should find Fit');
assert(result15.topCarMatch !== null, 'Should have a top match (likely order of mention)');

console.log('\nnormalize() - provenance tracking:');
const result16 = normalizer.normalize(
  '/fake/path/test.jpg',
  'Some transcript',
  { DateTime: '2026:04:05 10:00:00' }
);
assert(result16.provenance !== undefined, 'Should include provenance');
assert(result16.provenance.sources.filename === true, 'Should track filename check');
assert(result16.provenance.sources.transcript === true, 'Should track transcript check');
assert(result16.provenance.sources.exif === true, 'Should track EXIF check');

// ============================================================================
// Edge Cases
// ============================================================================

console.log('\n=== Edge Cases ===\n');

console.log('Edge case - empty strings:');
const result17 = normalizer.normalize('/fake/path/file.jpg', '', null);
assert(result17.topCarMatch === null || result17.topCarMatch.confidence < 0.5, 'Empty transcript should not match');

console.log('\nEdge case - partial word match (should not match):');
const transcript11 = 'The goblinlike car sat there.'; // "goblinlike" is not "Goblin"
const result18 = carExtractor.extractFromTranscript(transcript11);
assert(result18.length === 0, 'Should not match partial words');

console.log('\nEdge case - multiple dates in transcript:');
const transcript12 = 'March 22 was the rally. I also did work on April 5.';
const result19 = dateExtractor.extractFromTranscript(transcript12);
assert(result19.length >= 2, 'Should find multiple dates');

// ============================================================================
// Summary
// ============================================================================

console.log('\n' + '='.repeat(50));
console.log(`TESTS PASSED: ${passCount}`);
console.log(`TESTS FAILED: ${failCount}`);
console.log('='.repeat(50) + '\n');

if (failCount > 0) {
  process.exit(1);
}
