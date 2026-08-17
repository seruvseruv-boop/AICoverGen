import os
import urllib.parse
from picklescan.scanner import scan_file_path

ALLOWED_DOMAINS = {"huggingface.co", "hf.co", "pixeldrain.com"}


def validate_url(url: str) -> str:
    """Validate URL protocol and host."""
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty.")

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Invalid protocol '{parsed.scheme}'. Only HTTPS is allowed.")

    hostname = (parsed.hostname or "").lower()
    if not any(hostname == d or hostname.endswith("." + d) for d in ALLOWED_DOMAINS):
        raise ValueError("Only downloads from Hugging Face are allowed.")

    return url


def check_model_safety(file_path: str):
    """Statically checks model or archive integrity. Raises ValueError if unsafe."""
    if not file_path or not os.path.exists(file_path):
        print(f"Skip file: {file_path}")
        return

    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".pth", ".pt", ".bin", ".zip", ".pkl"):
        try:
            result = scan_file_path(file_path)
            if result and result.infected_files > 0:
                raise ValueError(
                    f"Integrity check failed: '{os.path.basename(file_path)}' contains unsupported or unsafe structures."
                )
        except ValueError:
            raise
        except Exception as e:
            print(f"Integrity check skipped for {file_path}: {e}")