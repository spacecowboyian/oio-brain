#!/usr/bin/env python3
"""
OIO Racing - Caption Validation and Quality Control

Validates generated captions against:
- Brand voice compliance (tone, terminology, style)
- Specificity requirements (car, driver, event details)
- Platform formatting (character limits, hashtag conventions)
- Content accuracy (verifiable facts match photo context)

Usage:
    python scripts/validate_captions.py --photo-dir photos/
    python scripts/validate_captions.py --input captions.json --output report.md

Output:
    - Detailed validation report with pass/fail for each caption
    - Brand voice compliance score
    - Specificity assessment
    - Recommendations for improvement
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime


class CaptionValidator:
    """Validates captions for brand voice, specificity, and quality."""

    def __init__(self, brain_root: Optional[Path] = None):
        """Initialize validator with OIO Brain context."""
        self.brain_root = brain_root or Path(__file__).parent.parent
        self.brand_voice = self._load_brand_voice()
        self.validation_results = []

    def _load_brand_voice(self) -> Dict[str, Any]:
        """Load brand voice documents for validation context."""
        voice_data = {
            "tone_keywords": [],
            "forbidden_terms": [],
            "required_elements": [],
            "hashtags": [],
            "voice_description": ""
        }

        # Load voice-and-tone.md
        voice_file = self.brain_root / "brand" / "voice-and-tone.md"
        if voice_file.exists():
            with open(voice_file) as f:
                content = f.read()
                voice_data["voice_description"] = content

                # Extract tone characteristics
                tone_section = self._extract_section(content, "tone|voice|personality")
                if tone_section:
                    voice_data["tone_keywords"] = self._extract_keywords(tone_section)

        # Load social-voice.md for platform-specific guidance
        social_file = self.brain_root / "brand" / "social-voice.md"
        if social_file.exists():
            with open(social_file) as f:
                content = f.read()
                voice_data["social_guidelines"] = content

        return voice_data

    def _extract_section(self, text: str, pattern: str) -> Optional[str]:
        """Extract a section from markdown text by header pattern."""
        pattern_re = re.compile(rf"^#+.*({pattern}).*$", re.MULTILINE | re.IGNORECASE)
        match = pattern_re.search(text)
        if not match:
            return None

        # Extract from header to next header or end
        start = match.start()
        next_header = re.search(r"\n^#+", text[match.end():])
        end = match.end() + next_header.start() if next_header else len(text)

        return text[start:end]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords/characteristics from text."""
        # Remove markdown syntax
        text = re.sub(r"[#*`\[\]]", "", text)
        # Extract words that appear multiple times (likely important)
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Filter out small words
                word_freq[word] = word_freq.get(word, 0) + 1

        return [w for w, count in word_freq.items() if count >= 2]

    def validate_caption(self, caption: str, context: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate a single caption.

        Args:
            caption: Caption text to validate
            context: Optional context about the photo (driver, car, event, etc.)

        Returns:
            Validation result with scores and recommendations
        """
        result = {
            "caption": caption[:100] + "..." if len(caption) > 100 else caption,
            "checks": {},
            "score": 0,
            "pass": True,
            "recommendations": []
        }

        # Brand voice checks
        result["checks"]["brand_voice"] = self._check_brand_voice(caption)
        # Specificity checks
        result["checks"]["specificity"] = self._check_specificity(caption, context)
        # Platform formatting checks
        result["checks"]["platform"] = self._check_platform_requirements(caption)
        # Length and structure checks
        result["checks"]["structure"] = self._check_caption_structure(caption)
        # Accuracy checks
        if context:
            result["checks"]["accuracy"] = self._check_accuracy(caption, context)

        # Calculate overall score
        checks = result["checks"]
        passed = sum(1 for c in checks.values() if c.get("pass", False))
        total = len(checks)
        result["score"] = int((passed / total) * 100)

        # Fail if critical checks don't pass
        if not checks.get("brand_voice", {}).get("pass", False):
            result["pass"] = False
            result["recommendations"].append("Caption does not match brand voice")

        if result["score"] < 80:
            result["pass"] = False

        return result

    def _check_brand_voice(self, caption: str) -> Dict[str, Any]:
        """Check caption against brand voice guidelines."""
        result = {"pass": True, "issues": []}

        caption_lower = caption.lower()

        # Check for brand-appropriate tone
        negative_indicators = ["spam", "buy now", "limited time", "exclusive offer"]
        for indicator in negative_indicators:
            if indicator in caption_lower:
                result["issues"].append(f"Contains salesy language: '{indicator}'")
                result["pass"] = False

        # Check for required Church of Combustion branding elements
        church_terms = ["combustion", "church", "reverend", "service"]
        has_brand_term = any(term in caption_lower for term in church_terms)

        # Church references are nice but not required in every caption
        if not has_brand_term and len(caption) > 100:
            result["issues"].append("Consider adding Church of Combustion branding for longer captions")

        # Check for exclamation mark appropriateness (1-2 max for brand voice)
        exclamation_count = caption.count("!")
        if exclamation_count > 2:
            result["issues"].append(f"Too many exclamation marks ({exclamation_count})")
            result["pass"] = False

        # Check hashtag quality
        hashtags = re.findall(r"#\w+", caption)
        if hashtags:
            # Verify hashtags match brand
            oio_hashtags = {"#churchofcombustion", "#oioracing", "#grassrootsmotorsports"}
            has_brand_hashtag = any(tag.lower() in oio_hashtags for tag in hashtags)
            if not has_brand_hashtag and len(hashtags) > 3:
                result["issues"].append("Consider including brand hashtags like #ChurchOfCombustion")

        return result

    def _check_specificity(self, caption: str, context: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Check caption includes specific details (car, driver, event)."""
        result = {"pass": True, "details_found": []}

        if not context:
            return result

        caption_lower = caption.lower()

        # Check for driver name
        if context.get("driver"):
            driver_lower = context["driver"].lower()
            if driver_lower in caption_lower:
                result["details_found"].append(f"driver: {context['driver']}")
            else:
                result["issues"] = result.get("issues", [])
                result["issues"].append(f"Driver name '{context['driver']}' not mentioned")

        # Check for car details
        if context.get("car"):
            car_lower = context["car"].lower()
            if car_lower in caption_lower or any(
                word in caption_lower
                for word in car_lower.split()
                if len(word) > 2
            ):
                result["details_found"].append(f"car: {context['car']}")

        # Check for event/context
        if context.get("event"):
            event_lower = context["event"].lower()
            if event_lower in caption_lower:
                result["details_found"].append(f"event: {context['event']}")

        # Specificity scoring
        required_details = ["driver", "car", "event"]
        available_details = [d for d in required_details if context.get(d)]
        if available_details:
            found_count = len(result["details_found"])
            specificity_score = found_count / len(available_details)
            if specificity_score < 0.66:
                result["pass"] = False

        return result

    def _check_platform_requirements(self, caption: str) -> Dict[str, Any]:
        """Check platform-specific formatting requirements."""
        result = {"pass": True, "issues": []}

        # Instagram: 2200 char limit
        if len(caption) > 2200:
            result["issues"].append(f"Caption exceeds Instagram limit (2200): {len(caption)} chars")
            result["pass"] = False

        # Twitter/X: 280 char limit (if short format)
        # This is for extended tweets, so we allow longer

        # Check hashtag count (optimal: 10-20 for IG)
        hashtags = re.findall(r"#\w+", caption)
        if len(hashtags) > 30:
            result["issues"].append(f"Too many hashtags ({len(hashtags)}). Optimal is 10-20.")
            result["pass"] = False
        elif len(hashtags) < 3:
            result["issues"].append("Consider adding more hashtags for discoverability")

        # Check for proper spacing around hashtags
        if "  #" in caption:
            result["issues"].append("Extra spacing before hashtags")

        # Check line breaks (captions should have readable structure)
        lines = caption.split("\n")
        if len(lines) == 1 and len(caption) > 200:
            result["issues"].append("Long caption with no line breaks - consider formatting")

        return result

    def _check_caption_structure(self, caption: str) -> Dict[str, Any]:
        """Check general caption structure and readability."""
        result = {"pass": True, "issues": []}

        # Check for opening hook/compelling first line
        first_sentence = caption.split("\n")[0].split(".")[0]
        if len(first_sentence) < 10:
            result["issues"].append("Opening line is too short - consider stronger hook")

        # Check grammar basics
        # Multiple exclamations/questions in a row
        if "!!!" in caption or "???" in caption:
            result["issues"].append("Avoid multiple punctuation marks (!!! or ???)")
            result["pass"] = False

        # Check for emoji usage (should be minimal and purposeful)
        emoji_count = len(re.findall(r"[😀-🙏🌀-🗿]", caption))
        if emoji_count > 5:
            result["issues"].append(f"Too many emojis ({emoji_count}). Keep to 1-3 for professionalism")

        # Check for all caps sections (should be minimal)
        all_caps = len(re.findall(r"\b[A-Z]{4,}\b", caption))
        if all_caps > 2:
            result["issues"].append(f"Too many all-caps words ({all_caps})")

        return result

    def _check_accuracy(self, caption: str, context: Dict[str, str]) -> Dict[str, Any]:
        """Check caption accuracy against photo context."""
        result = {"pass": True, "issues": []}

        caption_lower = caption.lower()

        # Verify mentioned facts match context
        if context.get("car") and context.get("car").lower() in caption_lower:
            # Double-check car details if mentioned
            if "miata" in caption_lower and context.get("car_model") == "Civic":
                result["issues"].append("Car model mismatch: caption mentions Miata but context shows Civic")
                result["pass"] = False

        if context.get("event") and context.get("event").lower() in caption_lower:
            # Check for event-specific details
            if "won" in caption_lower and not context.get("placed"):
                result["issues"].append("Caption claims victory but context doesn't confirm")

        return result

    def validate_batch(self, captions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of captions and generate summary report."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total": len(captions),
            "passed": 0,
            "failed": 0,
            "average_score": 0,
            "details": []
        }

        scores = []
        for caption_data in captions:
            caption = caption_data.get("text") or caption_data.get("caption")
            context = caption_data.get("context")

            validation = self.validate_caption(caption, context)
            validation["original"] = caption_data
            results["details"].append(validation)

            if validation["pass"]:
                results["passed"] += 1
            else:
                results["failed"] += 1

            scores.append(validation["score"])

        if scores:
            results["average_score"] = int(sum(scores) / len(scores))

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a markdown report from validation results."""
        report_lines = [
            "# Caption Validation Report",
            f"\nGenerated: {results['timestamp']}",
            f"\n## Summary",
            f"- **Total captions:** {results['total']}",
            f"- **Passed:** {results['passed']} ({int(results['passed']/results['total']*100)}%)",
            f"- **Failed:** {results['failed']} ({int(results['failed']/results['total']*100)}%)",
            f"- **Average score:** {results['average_score']}%",
        ]

        # Passed captions
        passed_captions = [d for d in results["details"] if d["pass"]]
        if passed_captions:
            report_lines.append("\n## ✅ Passed Captions")
            for i, detail in enumerate(passed_captions, 1):
                report_lines.append(f"\n### Caption {i} (Score: {detail['score']}%)")
                report_lines.append(f"*{detail['caption']}*")

        # Failed captions
        failed_captions = [d for d in results["details"] if not d["pass"]]
        if failed_captions:
            report_lines.append("\n## ❌ Failed Captions")
            for i, detail in enumerate(failed_captions, 1):
                report_lines.append(f"\n### Caption {i} (Score: {detail['score']}%)")
                report_lines.append(f"*{detail['caption']}*")
                if detail.get("recommendations"):
                    report_lines.append("\n**Recommendations:**")
                    for rec in detail["recommendations"]:
                        report_lines.append(f"- {rec}")

        # Issue summary
        all_issues = []
        for detail in results["details"]:
            for check_name, check_result in detail.get("checks", {}).items():
                if not check_result.get("pass", True):
                    all_issues.extend(check_result.get("issues", []))

        if all_issues:
            report_lines.append("\n## Common Issues")
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

            for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
                report_lines.append(f"- {issue} ({count} captions)")

        # Recommendations
        report_lines.append("\n## Overall Recommendations")
        if results["average_score"] >= 90:
            report_lines.append("✅ Captions are production-ready!")
        elif results["average_score"] >= 80:
            report_lines.append("⚠️ Captions are acceptable but could be improved.")
        else:
            report_lines.append("❌ Captions need significant revision before publication.")

        return "\n".join(report_lines)


def main():
    """CLI interface for caption validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate OIO Racing social media captions"
    )
    parser.add_argument(
        "--input",
        help="Input JSON file with captions"
    )
    parser.add_argument(
        "--output",
        help="Output report file (markdown)"
    )
    parser.add_argument(
        "--photo-dir",
        help="Directory with filed photos to validate captions for"
    )
    parser.add_argument(
        "--text",
        help="Single caption text to validate"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = CaptionValidator()

    # Single caption validation
    if args.text:
        result = validator.validate_caption(args.text)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["pass"] else 1)

    # Batch validation from JSON
    if args.input:
        with open(args.input) as f:
            captions = json.load(f)
        results = validator.validate_batch(captions)
    else:
        # Demo validation with sample captions
        sample_captions = [
            {
                "text": "Hudson dominating at KCRX Event 1! Won Novice class in the Civic. The Church of Combustion rolls on! 🏁 #ChurchOfCombustion #RallyCross #KCRX",
                "context": {"driver": "Hudson", "car": "Civic", "event": "KCRX E1"}
            },
            {
                "text": "Another great weekend!!!!!",
                "context": None
            },
        ]
        results = validator.validate_batch(sample_captions)

    # Generate report
    report = validator.generate_report(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"✅ Report saved to {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    sys.exit(0 if results["passed"] == results["total"] else 1)


if __name__ == "__main__":
    main()
