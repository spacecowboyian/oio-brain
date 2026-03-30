#!/usr/bin/env python3
"""
Test script for OIO Racing Caption Generation Service

Usage:
    # Start the service first in another terminal:
    python scripts/caption_generation_service.py

    # Then run this test:
    python scripts/test_caption_service.py
"""

import requests
import json
import sys

CAPTION_SERVICE_URL = "http://localhost:5000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{CAPTION_SERVICE_URL}/health", timeout=5)
        response.raise_for_status()
        print("✓ Health check passed")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_caption_generation():
    """Test caption generation endpoint."""
    print("\nTesting caption generation...")

    # Example request
    payload = {
        "media_urls": ["https://example.com/race-photo.jpg"],
        "context": "KCRX Event 1 at Ray Rocks. Hudson won Novice class. The Goblin had a bearing failure after 6 runs.",
        "caption_count": 3
    }

    try:
        print(f"Sending request: {json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{CAPTION_SERVICE_URL}/generate-caption",
            json=payload,
            timeout=180  # 3 minutes timeout for AI generation
        )
        response.raise_for_status()

        result = response.json()
        print("✓ Caption generation completed")
        print(f"\nGenerated captions:")
        print(json.dumps(result, indent=2))

        # Validate response structure
        assert "captions" in result, "Response missing 'captions' field"
        assert "task_id" in result, "Response missing 'task_id' field"
        assert len(result["captions"]) > 0, "No captions generated"

        print(f"\n✓ Generated {len(result['captions'])} caption(s)")
        for i, caption in enumerate(result["captions"], 1):
            print(f"\nCaption {i}:")
            print(f"  Text: {caption.get('text', 'N/A')}")
            print(f"  Hashtags: {', '.join(caption.get('hashtags', []))}")
            print(f"  Length: {caption.get('char_count', 'N/A')} characters")

        return True

    except requests.Timeout:
        print("✗ Request timed out (this is normal for first run - AI takes time)")
        print("  Check the service logs to see task progress")
        return False
    except Exception as e:
        print(f"✗ Caption generation failed: {e}")
        if hasattr(e, 'response'):
            print(f"  Response: {e.response.text}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("OIO Racing Caption Generation Service - Test Suite")
    print("=" * 60)

    # Check if service is running
    if not test_health():
        print("\n⚠️  Service is not running.")
        print("Start it with: python scripts/caption_generation_service.py")
        sys.exit(1)

    # Test caption generation
    success = test_caption_generation()

    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        print("\nNote: Caption generation requires:")
        print("  1. Caption service running (python scripts/caption_generation_service.py)")
        print("  2. Paperclip API accessible")
        print("  3. AI Copywriter agent available")
        print("  4. Valid PAPERCLIP_API_KEY and PAPERCLIP_COMPANY_ID")
    print("=" * 60)


if __name__ == "__main__":
    main()
