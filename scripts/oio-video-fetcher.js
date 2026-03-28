// OIO Racing - YouTube Video Fetcher
// Run with: node scripts/oio-video-fetcher.js
// Requires Node.js (no extra packages needed - uses built-in https)
// Requires environment variable: YOUTUBE_API_KEY

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_KEY = process.env.YOUTUBE_API_KEY;
const CHANNEL_ID = 'UCA6AlnPQNu5u3Clq_hEmBKQ'; // retained for reference; playlist ID is derived from this
const UPLOADS_PLAYLIST = 'UUA6AlnPQNu5u3Clq_hEmBKQ';
const OUTPUT_FILE = path.join(__dirname, '..', 'oio_videos_raw.json');

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

async function fetchAllVideos() {
  console.log('Fetching all videos from OIO Racing channel...');
  let videos = [];
  let nextPageToken = null;
  let page = 1;

  do {
    let url = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=${UPLOADS_PLAYLIST}&key=${API_KEY}`;
    if (nextPageToken) url += `&pageToken=${nextPageToken}`;

    console.log(`  Fetching page ${page}...`);
    const data = await fetchJson(url);

    if (data.error) {
      console.error('API Error:', data.error.message);
      process.exit(1);
    }

    for (const item of data.items) {
      videos.push({
        videoId: item.snippet.resourceId.videoId,
        title: item.snippet.title,
        publishedAt: item.snippet.publishedAt.substring(0, 10),
        description: item.snippet.description || ''
      });
    }

    nextPageToken = data.nextPageToken || null;
    page++;
  } while (nextPageToken);

  console.log(`  Got ${videos.length} videos. Fetching full details + stats...`);

  // Fetch stats and tags in batches of 50
  const detailed = [];
  for (let i = 0; i < videos.length; i += 50) {
    const chunk = videos.slice(i, i + 50);
    const ids = chunk.map(v => v.videoId).join(',');
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
    console.log(`  Detailed: ${Math.min(i + 50, videos.length)}/${videos.length}`);
  }

  // Sort by date descending
  detailed.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(detailed, null, 2));
  console.log(`\nDone! Saved ${detailed.length} videos to: ${OUTPUT_FILE}`);
  console.log('\nTop 5 most viewed:');
  [...detailed].sort((a, b) => b.viewCount - a.viewCount).slice(0, 5).forEach(v => {
    console.log(`  ${v.viewCount.toLocaleString()} views - ${v.title}`);
  });
}

fetchAllVideos().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
