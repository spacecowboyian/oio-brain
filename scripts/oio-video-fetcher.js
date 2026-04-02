// OIO Racing - YouTube Video Fetcher
// Run with: node scripts/oio-video-fetcher.js
// Requires Node.js (no extra packages needed - uses built-in https)
// Requires environment variable: YOUTUBE_API_KEY
//
// Behavior:
//   - Reads the existing master video JSON from content/oio-videos-master.json
//   - Fetches all current video IDs from the YouTube uploads playlist
//   - Detects new videos not yet in the master and fetches their full details
//   - Refreshes view/like/comment counts for all existing videos
//   - Saves the full updated master back in place
//   - If new videos were found, writes them to intake/docs/oio_videos_raw.json
//     so the Copilot agent can process just the delta into the brain files

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.YOUTUBE_API_KEY;
const CHANNEL_ID = 'UCA6AlnPQNu5u3Clq_hEmBKQ'; // retained for reference; playlist ID is derived from this
const UPLOADS_PLAYLIST = 'UUA6AlnPQNu5u3Clq_hEmBKQ';

const MASTER_FILE = path.join(__dirname, '..', 'content', 'oio-videos-master.json');
const DOCDUMP_FILE = path.join(__dirname, '..', 'intake', 'docs', 'oio_videos_raw.json');

if (!API_KEY) {
  console.error('Error: YOUTUBE_API_KEY environment variable is not set.');
  process.exit(1);
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode < 200 || res.statusCode >= 300) {
          return reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    }).on('error', reject);
  });
}

function loadMaster() {
  if (fs.existsSync(MASTER_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(MASTER_FILE, 'utf8'));
    } catch (e) {
      console.warn('Warning: could not parse master file, starting fresh.');
    }
  }
  console.log('No master file found — will do a full fetch on first run.');
  return [];
}

async function fetchPlaylistVideoIds() {
  console.log('Fetching video IDs from uploads playlist...');
  const ids = [];
  let nextPageToken = null;
  let page = 1;

  do {
    let url = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=${UPLOADS_PLAYLIST}&key=${API_KEY}`;
    if (nextPageToken) url += `&pageToken=${nextPageToken}`;

    console.log(`  Page ${page}...`);
    const data = await fetchJson(url);

    if (data.error) {
      console.error('API Error:', data.error.message);
      process.exit(1);
    }

    for (const item of data.items) {
      ids.push(item.snippet.resourceId.videoId);
    }

    nextPageToken = data.nextPageToken || null;
    page++;
  } while (nextPageToken);

  return ids;
}

async function fetchVideoDetails(videoIds) {
  const detailed = [];
  for (let i = 0; i < videoIds.length; i += 50) {
    const chunk = videoIds.slice(i, i + 50);
    const ids = chunk.join(',');
    const url = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=${ids}&key=${API_KEY}`;
    const data = await fetchJson(url);

    for (const item of data.items) {
      detailed.push({
        videoId: item.id,
        title: item.snippet.title,
        publishedAt: item.snippet.publishedAt.substring(0, 10),
        description: item.snippet.description || '',
        tags: (item.snippet.tags || []).join(', '),
        duration: item.contentDetails.duration,
        viewCount: parseInt(item.statistics.viewCount || 0),
        likeCount: parseInt(item.statistics.likeCount || 0),
        commentCount: parseInt(item.statistics.commentCount || 0),
        url: `https://www.youtube.com/watch?v=${item.id}`
      });
    }
    console.log(`  Details fetched: ${Math.min(i + 50, videoIds.length)}/${videoIds.length}`);
  }
  return detailed;
}

async function run() {
  const master = loadMaster();
  const masterById = new Map(master.map(v => [v.videoId, v]));

  const allIds = await fetchPlaylistVideoIds();
  console.log(`  ${allIds.length} total videos on channel`);

  const newIds = allIds.filter(id => !masterById.has(id));
  const existingIds = allIds.filter(id => masterById.has(id));

  console.log(`  New videos: ${newIds.length}`);
  console.log(`  Existing videos (stats refresh): ${existingIds.length}`);

  // Fetch details for new videos
  let newVideos = [];
  if (newIds.length > 0) {
    console.log('\nFetching full details for new videos...');
    newVideos = await fetchVideoDetails(newIds);
    for (const v of newVideos) {
      masterById.set(v.videoId, v);
    }
  }

  // Refresh stats for existing videos in batches
  if (existingIds.length > 0) {
    console.log('\nRefreshing stats for existing videos...');
    const refreshed = await fetchVideoDetails(existingIds);
    for (const v of refreshed) {
      const existing = masterById.get(v.videoId);
      if (existing) {
        existing.viewCount = v.viewCount;
        existing.likeCount = v.likeCount;
        existing.commentCount = v.commentCount;
      }
    }
  }

  // Rebuild full list sorted by date descending
  const updated = Array.from(masterById.values());
  updated.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));

  // Save updated master
  fs.mkdirSync(path.dirname(MASTER_FILE), { recursive: true });
  fs.writeFileSync(MASTER_FILE, JSON.stringify(updated, null, 2));
  console.log(`\nMaster updated: ${updated.length} videos → ${MASTER_FILE}`);

  // Write delta to intake/docs only if there are new videos
  if (newVideos.length > 0) {
    newVideos.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
    fs.mkdirSync(path.dirname(DOCDUMP_FILE), { recursive: true });
    fs.writeFileSync(DOCDUMP_FILE, JSON.stringify(newVideos, null, 2));
    console.log(`\n${newVideos.length} new video(s) written to intake/docs for agent processing:`);
    newVideos.forEach(v => console.log(`  + [${v.publishedAt}] ${v.title}`));
  } else {
    console.log('\nNo new videos found. intake/docs not written.');
  }

  console.log('\nTop 5 most viewed:');
  [...updated].sort((a, b) => b.viewCount - a.viewCount).slice(0, 5).forEach(v => {
    console.log(`  ${v.viewCount.toLocaleString()} views - ${v.title}`);
  });
}

run().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
