# OIO Racing - Caption Generation Service

## Overview

The Caption Generation Service is an AI-powered tool that generates social media captions for OIO Racing posts. It integrates:

- **PostBridge**: Media management and social account integration
- **OIO Brain**: Brand voice guidelines and contextual racing information
- **AI Copywriter Agent**: Paperclip agent that drafts captions following brand voice
- **Flask API**: Simple HTTP endpoint for caption generation

## Architecture

```
┌─────────────────┐
│  Slackbot or    │
│  External Client│
└────────┬────────┘
         │
         │ POST /generate-caption
         ▼
┌─────────────────────────────────┐
│  Caption Generation Service     │
│  (Flask API)                    │
├─────────────────────────────────┤
│  1. Read brand voice docs       │
│  2. Query OIO Brain context     │
│  3. Create Paperclip task       │
│  4. Poll for completion         │
└────────┬────────────────────────┘
         │
         │ Create task
         ▼
┌─────────────────────────────────┐
│  Paperclip API                  │
│  ├─ AI Copywriter Agent         │
│  └─ Task Management             │
└────────┬────────────────────────┘
         │
         │ Return captions
         ▼
┌─────────────────────────────────┐
│  Response with caption options  │
└─────────────────────────────────┘
```

## Installation

### Prerequisites

1. Python 3.8+ with required packages:
   ```bash
   pip install flask requests
   ```

2. Environment variables:
   ```bash
   export PAPERCLIP_API_KEY="your-paperclip-api-key"
   export PAPERCLIP_API_URL="http://127.0.0.1:3100"
   export PAPERCLIP_COMPANY_ID="your-company-id"
   export POSTBRIDGE_API_KEY="your-postbridge-api-key"  # Optional, for future integration
   ```

3. Running Paperclip instance with AI Copywriter agent

## Usage

### Starting the Service

```bash
# Start the Flask API server
python scripts/caption_generation_service.py
```

The service will start on `http://localhost:5000` by default.

To use a different port:
```bash
export CAPTION_SERVICE_PORT=8080
python scripts/caption_generation_service.py
```

### API Endpoints

#### POST `/generate-caption`

Generate social media captions for a post.

**Request:**
```json
{
  "media_ids": ["postbridge-media-id-1", "postbridge-media-id-2"],
  "media_urls": ["https://example.com/race-photo.jpg"],
  "context": "KCRX Event 1 at Ray Rocks. Hudson won Novice class. The Goblin had a bearing failure after 6 runs.",
  "caption_count": 3
}
```

**Parameters:**
- `media_ids` (optional): Array of PostBridge media IDs
- `media_urls` (optional): Array of public image/video URLs
- `context` (optional): Additional context about the event, race results, or car details
- `caption_count` (optional): Number of caption variations to generate (default: 3)

**Note:** Either `media_ids` or `media_urls` must be provided.

**Response:**
```json
{
  "captions": [
    {
      "text": "Hudson won Novice at KCRX E1. First trophy of the season. The congregation is proud. #ChurchOfCombustion #RallyCross #KCRX",
      "hashtags": ["#ChurchOfCombustion", "#RallyCross", "#KCRX"],
      "char_count": 125
    },
    {
      "text": "The Goblin didn't survive E1. Bearing failure, cyl 4 at 35 PSI. But Hudson grabbed his first Novice win. Season's not over. #GrassrootsRacing #KCRX",
      "hashtags": ["#GrassrootsRacing", "#KCRX"],
      "char_count": 150
    },
    {
      "text": "Sunday service at Ray Rocks. Hudson's first trophy. The Goblin's final sermon before the bearing failure. Amen. #ChurchOfCombustion",
      "hashtags": ["#ChurchOfCombustion"],
      "char_count": 134
    }
  ],
  "brand_voice_applied": true,
  "context_sources": [
    "01 - Brand/Voice-and-Tone.md",
    "02 - Content/OIO-Brand-Voice-Guide.md",
    "03 - Cars/Ian/1985 MR2/Overview.md"
  ],
  "task_id": "756d8584-1564-46dd-a7c6-0e92eefaaf24"
}
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "OIO Racing Caption Generation Service",
  "ai_copywriter_agent_id": "a2859bcb-cb20-4429-916b-65401f66d96a"
}
```

### Example Usage

#### Using curl

```bash
curl -X POST http://localhost:5000/generate-caption \
  -H "Content-Type: application/json" \
  -d '{
    "media_urls": ["https://example.com/race-photo.jpg"],
    "context": "KCRX Event 1, Hudson won Novice",
    "caption_count": 3
  }'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:5000/generate-caption",
    json={
        "media_urls": ["https://example.com/race-photo.jpg"],
        "context": "KCRX Event 1, Hudson won Novice class",
        "caption_count": 3
    },
    timeout=180
)

result = response.json()
for caption in result["captions"]:
    print(f"Caption: {caption['text']}")
    print(f"Hashtags: {', '.join(caption['hashtags'])}")
    print()
```

#### Testing

Run the included test suite:

```bash
# Make sure service is running first
python scripts/caption_generation_service.py

# In another terminal, run tests
python scripts/test_caption_service.py
```

## How It Works

### 1. Brand Voice Context

The service reads two key brand voice documents:
- `OIO Brain/01 - Brand/Voice-and-Tone.md` - Core voice qualities
- `OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md` - Social media-specific guidelines

These provide the AI Copywriter with:
- Tone guidelines (conversational, self-aware, encouraging)
- Vocabulary patterns (congregation, Sunday service, etc.)
- Car nicknames (Goblin, Fitty Cent, Dale, etc.)
- Do/Don't examples
- Hashtag strategy

### 2. OIO Brain Context Retrieval

The service searches OIO Brain for relevant context:

**Car Information:**
- Searches `03 - Cars/` for mentioned vehicles
- Extracts car details, modifications, current status

**Recent Events:**
- Searches `02 - Content/Summaries/` for race event recaps
- Includes most recent 3 event summaries

**Keywords Detected:**
- Car names: goblin, fitty cent, dale, nessie, etc.
- Event types: autocross, rallycross, track day
- Locations: Ray Rocks, Lake Garnett, Arrowhead

### 3. AI Copywriter Integration

The service creates a Paperclip task assigned to the AI Copywriter agent:

1. **Task Creation**: Posts task to `/api/companies/{companyId}/issues`
2. **Task Assignment**: Auto-assigned to AI Copywriter agent
3. **Polling**: Polls task status every 5 seconds (max 2 minutes)
4. **Response Extraction**: Parses JSON captions from task comments

### 4. Caption Format

Generated captions follow this structure:
```json
{
  "text": "Caption text with hashtags",
  "hashtags": ["#ChurchOfCombustion", "#RallyCross"],
  "char_count": 150
}
```

**Character Limits:**
- Instagram: 2,200 characters (but 1-3 sentences recommended)
- Facebook: 63,206 characters (but brevity preferred)
- Practical limit: 150-250 characters for best engagement

## Integration with Slackbot

The Caption Generation Service is designed to integrate with the Slackbot (OUT-73):

```
User in Slack:
  /post-caption <media-url> Context: KCRX E1 results

Slackbot:
  1. Calls Caption Generation Service API
  2. Shows caption options to user
  3. User selects preferred caption
  4. Slackbot creates PostBridge draft with selected caption
```

This enables mobile-first social media workflow:
1. Take photo at track
2. Request captions in Slack
3. Review and approve from phone
4. Publish or schedule post

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PAPERCLIP_API_KEY` | Yes | - | Paperclip API authentication key |
| `PAPERCLIP_API_URL` | Yes | `http://127.0.0.1:3100` | Paperclip API base URL |
| `PAPERCLIP_COMPANY_ID` | Yes | - | Paperclip company ID |
| `POSTBRIDGE_API_KEY` | No | - | PostBridge API key (future use) |
| `CAPTION_SERVICE_PORT` | No | `5000` | Flask server port |

## Troubleshooting

### Service won't start

**Error:** `PAPERCLIP_API_KEY not set`

**Solution:** Export required environment variables:
```bash
export PAPERCLIP_API_KEY="your-key"
export PAPERCLIP_COMPANY_ID="your-company-id"
```

### Caption generation times out

**Error:** `Caption generation timed out after 120 seconds`

**Possible causes:**
1. AI Copywriter agent is busy with other tasks
2. Paperclip heartbeat is not running
3. Agent is paused or offline

**Solution:**
- Check AI Copywriter agent status in Paperclip
- Verify agent heartbeat is enabled
- Increase timeout in service configuration

### No captions returned

**Error:** `No captions found in task response`

**Possible causes:**
1. AI Copywriter didn't format response as JSON
2. Task failed or was blocked
3. Agent returned text instead of structured JSON

**Solution:**
- Check Paperclip task comments manually
- Verify AI Copywriter agent has proper instructions
- Review task status and error messages

### Brand voice not applied correctly

**Issue:** Generated captions don't match OIO voice

**Solution:**
1. Verify brand voice documents exist:
   - `OIO Brain/01 - Brand/Voice-and-Tone.md`
   - `OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md`
2. Check AI Copywriter agent instructions
3. Provide more specific context in request

## Future Enhancements

- [ ] Direct PostBridge media fetching via API
- [ ] Caption history and analytics
- [ ] A/B testing for caption variations
- [ ] Real-time caption refinement (user feedback loop)
- [ ] Integration with social media analytics
- [ ] Automated hashtag suggestions based on trending topics
- [ ] Multi-platform caption optimization (Instagram vs Facebook)

## Related Documentation

- [PostBridge Client Library](../scripts/postbridge_client.py)
- [OIO Brand Voice Guide](../OIO%20Brain/02%20-%20Content/OIO-Brand-Voice-Guide.md)
- [Social Media Workflow](../OIO%20Brain/00%20-%20Start%20Here/OIO-Operating-System.md)

## Support

For issues or questions:
1. Check Paperclip task logs: `/OUT/issues/<task-id>`
2. Review service logs for error details
3. Verify all environment variables are set
4. Ensure Paperclip and AI Copywriter agent are running
