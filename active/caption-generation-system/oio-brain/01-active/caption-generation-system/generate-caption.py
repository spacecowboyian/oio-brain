#!/usr/bin/env python3
"""
OIO Caption Generation System

Generates social media captions using Claude API that match OIO Racing's
grassroots voice and brand personality.

Usage:
    python generate-caption.py --input "Video description here"
    python generate-caption.py --batch --input test-descriptions.json
    python generate-caption.py --interactive

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY="your-key-here"
"""

import anthropic
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime


class OIOCaptionGenerator:
    """Caption generator for OIO Racing social media posts."""

    def __init__(self, api_key=None):
        """Initialize the caption generator."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"

        # Load system prompt and few-shot examples
        script_dir = Path(__file__).parent
        self.system_prompt = self._load_file(script_dir / "system-prompt.md")
        self.few_shot_examples = self._load_file(script_dir / "few-shot-examples.md")

    def _load_file(self, filepath):
        """Load content from a file."""
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: {filepath} not found")
            sys.exit(1)

    def generate_caption(self, video_description, video_title=None, cars=None,
                        content_type=None, tone_preference=None, variations=3):
        """
        Generate caption options for a video description.

        Args:
            video_description: Description of the video content
            video_title: Optional video title
            cars: Optional list of cars featured
            content_type: Optional content type (Video Tease, Build Update, etc.)
            tone_preference: Optional tone bucket preference
            variations: Number of caption variations to generate (default: 3)

        Returns:
            dict: Generated captions with metadata
        """
        # Build the user prompt
        user_prompt = self._build_user_prompt(
            video_description, video_title, cars, content_type, tone_preference, variations
        )

        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            response_text = message.content[0].text

            return {
                "input": {
                    "video_description": video_description,
                    "video_title": video_title,
                    "cars": cars,
                    "content_type": content_type,
                    "tone_preference": tone_preference
                },
                "captions": response_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            sys.exit(1)

    def _build_user_prompt(self, video_description, video_title, cars,
                          content_type, tone_preference, variations):
        """Build the user prompt for caption generation."""
        prompt_parts = [
            "Generate social media captions for the following OIO Racing content:\n"
        ]

        if video_title:
            prompt_parts.append(f"**Video Title:** {video_title}\n")

        prompt_parts.append(f"**Description:** {video_description}\n")

        if cars:
            cars_str = ", ".join(cars)
            prompt_parts.append(f"**Cars Featured:** {cars_str}\n")

        if content_type:
            prompt_parts.append(f"**Content Type:** {content_type}\n")

        if tone_preference:
            prompt_parts.append(f"**Preferred Tone:** {tone_preference}\n")

        prompt_parts.append(f"\nGenerate {variations} caption options following OIO voice guidelines.")
        prompt_parts.append("\nFor each option, provide:")
        prompt_parts.append("1. Caption text with appropriate hashtags")
        prompt_parts.append("2. Tone bucket classification")
        prompt_parts.append("3. Character count")
        prompt_parts.append("4. Brief rationale (1-2 sentences)")
        prompt_parts.append("\nRefer to the few-shot examples below for patterns:\n")
        prompt_parts.append(f"\n---\n{self.few_shot_examples}\n---\n")

        return "\n".join(prompt_parts)

    def batch_generate(self, test_file_path, output_file=None):
        """
        Generate captions for all test descriptions in a JSON file.

        Args:
            test_file_path: Path to JSON file with test descriptions
            output_file: Optional output file path (default: auto-generated)
        """
        # Load test descriptions
        try:
            with open(test_file_path, 'r') as f:
                test_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: {test_file_path} not found")
            sys.exit(1)

        descriptions = test_data.get("test_descriptions", [])
        results = []

        print(f"Processing {len(descriptions)} test descriptions...")

        for i, desc in enumerate(descriptions, 1):
            print(f"\nGenerating captions for test {i}/{len(descriptions)}: {desc.get('video_title', 'Untitled')}")

            result = self.generate_caption(
                video_description=desc.get("description", ""),
                video_title=desc.get("video_title"),
                cars=desc.get("cars"),
                content_type=desc.get("content_type"),
                tone_preference=desc.get("expected_tone"),
                variations=3
            )

            result["test_id"] = desc.get("id")
            result["key_details"] = desc.get("key_details")
            results.append(result)

            print(f"✓ Generated {3} caption options")

        # Save results
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f"caption-generation-results-{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_tests": len(descriptions),
                "model": self.model,
                "results": results
            }, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")
        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate OIO Racing social media captions using Claude API"
    )
    parser.add_argument(
        "--input",
        help="Video description text or path to test JSON file"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process batch of test descriptions from JSON file"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode - prompt for input"
    )
    parser.add_argument(
        "--title",
        help="Video title (single caption mode only)"
    )
    parser.add_argument(
        "--cars",
        help="Comma-separated list of cars featured"
    )
    parser.add_argument(
        "--type",
        help="Content type (Video Tease, Build Update, etc.)"
    )
    parser.add_argument(
        "--tone",
        help="Preferred tone bucket"
    )
    parser.add_argument(
        "--output",
        help="Output file path (batch mode only)"
    )
    parser.add_argument(
        "--variations",
        type=int,
        default=3,
        help="Number of caption variations (default: 3)"
    )

    args = parser.parse_args()

    # Initialize generator
    try:
        generator = OIOCaptionGenerator()
    except ValueError as e:
        print(f"Error: {e}")
        print("Set ANTHROPIC_API_KEY environment variable first")
        sys.exit(1)

    # Interactive mode
    if args.interactive:
        print("=== OIO Caption Generator (Interactive Mode) ===\n")
        video_description = input("Enter video description: ").strip()
        video_title = input("Enter video title (optional): ").strip() or None
        cars_input = input("Enter cars (comma-separated, optional): ").strip()
        cars = [c.strip() for c in cars_input.split(",")] if cars_input else None

        print("\nGenerating captions...")
        result = generator.generate_caption(
            video_description=video_description,
            video_title=video_title,
            cars=cars,
            variations=args.variations
        )

        print("\n" + "="*80)
        print(result["captions"])
        print("="*80)
        return

    # Batch mode
    if args.batch:
        if not args.input:
            print("Error: --input required for batch mode")
            sys.exit(1)

        generator.batch_generate(args.input, args.output)
        return

    # Single caption mode
    if not args.input:
        print("Error: --input required (or use --interactive)")
        parser.print_help()
        sys.exit(1)

    # Check if input is a file
    if os.path.isfile(args.input):
        print("Error: Use --batch flag to process JSON files")
        sys.exit(1)

    # Generate single caption
    cars = [c.strip() for c in args.cars.split(",")] if args.cars else None

    print("Generating captions...")
    result = generator.generate_caption(
        video_description=args.input,
        video_title=args.title,
        cars=cars,
        content_type=args.type,
        tone_preference=args.tone,
        variations=args.variations
    )

    print("\n" + "="*80)
    print(result["captions"])
    print("="*80)


if __name__ == "__main__":
    main()
