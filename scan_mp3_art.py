import os
import json
import argparse
from mutagen.id3 import ID3
from mutagen.mp3 import MP3


def has_valid_album_art(file_path):
    """
    Returns True if the MP3 has at least one valid embedded image (APIC frame).
    """
    try:
        tags = ID3(file_path)
        for tag in tags.values():
            if tag.FrameID == "APIC" and getattr(tag, "data", None):
                return True
        return False
    except Exception:
        return False


def get_tag_info(file_path):
    """
    Extract artist and title safely.
    """
    try:
        audio = MP3(file_path)
        tags = audio.tags

        artist = tags.get("TPE1")
        title = tags.get("TIT2")

        return {
            "artist": artist.text[0] if artist else None,
            "title": title.text[0] if title else None,
        }
    except Exception:
        return {
            "artist": None,
            "title": None,
        }


def scan_directory(root_dir):
    """
    Walk directory recursively and collect MP3s missing album art.
    """
    results = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if not file.lower().endswith(".mp3"):
                continue

            full_path = os.path.join(root, file)

            if not has_valid_album_art(full_path):
                tag_info = get_tag_info(full_path)

                results.append({
                    "path": full_path,
                    "artist": tag_info["artist"],
                    "title": tag_info["title"],
                })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Scan MP3 files and find ones missing embedded album art."
    )
    parser.add_argument("directory", help="Root directory to scan")
    parser.add_argument(
        "-o",
        "--output",
        default="missing_art.json",
        help="Output JSON file (default: missing_art.json)",
    )

    args = parser.parse_args()

    print(f"🔍 Scanning: {args.directory}")
    results = scan_directory(args.directory)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. Found {len(results)} files without album art.")
    print(f"📄 Results saved to: {args.output}")


if __name__ == "__main__":
    main()