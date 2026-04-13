# OIO Caption Generation System

**Status:** Phase 3 Implementation
**Owner:** AI Copywriter
**Issue:** OUT-98
**Created:** 2026-03-30

## Overview

This directory contains the AI-powered caption generation system for OIO Racing social media posts. The system uses Claude API to generate captions that match OIO's grassroots racing voice while maintaining authenticity and engagement.

## Components

1. **`system-prompt.md`** - Core Claude system prompt incorporating brand voice guidelines
2. **`few-shot-examples.md`** - Curated top-performing posts for few-shot learning
3. **`test-descriptions.json`** - 20 test video descriptions for validation
4. **`generate-caption.py`** - Python script for caption generation via Claude API
5. **`quality-criteria.md`** - Quality assessment rubric and tuning guidelines
6. **`ab-testing-framework.md`** - A/B testing methodology and tracking

## Quick Start

```bash
# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Generate captions
python generate-caption.py --input "Video description here"

# Run batch test
python generate-caption.py --batch --input test-descriptions.json
```

## Success Criteria

- >90% caption approval rate on first generation
- Captions match OIO brand voice on manual review
- Character limits: Instagram 2200, Facebook 63,206 (aim for <300)
- Support multiple caption variations per input

## References

- Brand Voice Guide: `OIO Brain/01 - Brand/Social-Post-Voice.md`
- Social Post Archive: `OIO Brain/data/social-posts/`
- Caption Drafts: `OIO Brain/02 - Content/Caption-Drafts/`
