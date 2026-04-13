# OIO Caption Generation System - Setup Guide

## Prerequisites

- Python 3.8 or higher
- Claude API key from Anthropic

## Installation Steps

### 1. Install Python Dependencies

```bash
cd oio-brain/01-active/caption-generation-system
pip install -r requirements.txt
```

Or install directly:
```bash
pip install anthropic
```

### 2. Set Up API Key

Get your Claude API key from: https://console.anthropic.com/

Set as environment variable:

```bash
# macOS/Linux
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows
set ANTHROPIC_API_KEY=your-api-key-here
```

Or add to your shell profile for persistence:

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Setup

Test that the system can load files and initialize:

```bash
python generate-caption.py --help
```

You should see the help message with usage instructions.

## Quick Start Examples

### Generate Single Caption

```bash
python generate-caption.py \
  --input "The Goblin MR2 has been losing compression on cylinder 4. Time to tear down the 4AGE and see what's broken." \
  --title "AW11 MR2 Engine Teardown" \
  --cars "Goblin MR2" \
  --type "Build Update"
```

### Interactive Mode

```bash
python generate-caption.py --interactive
```

Follow the prompts to enter video details.

### Batch Generation (Test All 20 Descriptions)

```bash
python generate-caption.py --batch --input test-descriptions.json
```

This will generate captions for all 20 test descriptions and save results to a timestamped JSON file.

### Batch with Custom Output File

```bash
python generate-caption.py \
  --batch \
  --input test-descriptions.json \
  --output my-results.json
```

## Output Format

### Single Caption Output

The script will print 3-4 caption options directly to the console:

```
================================================================================
## Option 1: [Tone Bucket]

[Caption text with hashtags]

**Character Count:** 123
**Rationale:** [Why this works]

---

## Option 2: [Tone Bucket]
...
================================================================================
```

### Batch Output JSON

Batch results are saved to JSON file:

```json
{
  "generated_at": "2026-03-30T10:00:00",
  "total_tests": 20,
  "model": "claude-sonnet-4-5",
  "results": [
    {
      "test_id": 1,
      "input": {
        "video_description": "...",
        "video_title": "...",
        "cars": ["Goblin MR2"]
      },
      "captions": "... generated caption options ...",
      "timestamp": "2026-03-30T10:00:15"
    }
  ]
}
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

Install the anthropic package:
```bash
pip install anthropic
```

### "ValueError: ANTHROPIC_API_KEY environment variable not set"

Set your API key as environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Error: system-prompt.md not found"

Make sure you're running the script from the `caption-generation-system` directory, or the files are in the correct location.

### API Rate Limiting

If you hit rate limits during batch processing, you can:
1. Reduce batch size
2. Add delays between requests
3. Use a higher tier API key

## File Structure

```
caption-generation-system/
├── README.md                      # Overview and quick start
├── SETUP.md                       # This file - setup instructions
├── requirements.txt               # Python dependencies
├── system-prompt.md               # Core AI system prompt
├── few-shot-examples.md          # Example posts for training
├── test-descriptions.json         # 20 test video descriptions
├── quality-criteria.md            # Quality rubric and tuning
├── ab-testing-framework.md        # A/B testing methodology
└── generate-caption.py            # Main generation script
```

## Next Steps

After setup:

1. **Run Test Batch** - Generate captions for all 20 test descriptions
2. **Review Quality** - Score generated captions using quality-criteria.md rubric
3. **Tune System** - Adjust system prompt or parameters based on results
4. **Start A/B Testing** - Use ab-testing-framework.md to validate performance

## API Costs

Claude API pricing (as of 2026-03):
- **Sonnet 4.5**: ~$3 per million input tokens, ~$15 per million output tokens

**Estimated cost per caption:**
- System prompt: ~3,000 tokens (input)
- Few-shot examples: ~2,500 tokens (input)
- User prompt: ~200 tokens (input)
- Output: ~300 tokens
- **Total per caption:** ~$0.02

**Batch of 20 test descriptions:** ~$0.40

## Support

For issues or questions:
- Check quality-criteria.md for tuning guidance
- Review few-shot-examples.md for voice patterns
- Refer to system-prompt.md for AI instructions
- See ab-testing-framework.md for validation methodology
