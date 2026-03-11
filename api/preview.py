import base64
import io
from typing import Any

# Example imports; adjust to your real package structure
# from response_stats.pipeline import run_pipeline
# from response_stats.config import Config

def fig_to_base64_png(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def generate_preview(sample_size: int, threshold: float, scale: float, seed: int) -> dict[str, Any]:
    """
    Thin wrapper around your existing generator.
    Return JSON-friendly data for the frontend.
    """

    # Replace this with your real generation code.
    #
    # Example shape:
    #
    # cfg = Config(
    #     sample_size=sample_size,
    #     threshold=threshold,
    #     scale=scale,
    #     seed=seed,
    # )
    # output = run_pipeline(cfg, preview=True)
    # fig = output.figure
    # image_b64 = fig_to_base64_png(fig)
    # stats = output.stats

    # Placeholder response for wiring everything up first:
    stats = {
        "sample_size": sample_size,
        "threshold": threshold,
        "scale": scale,
        "seed": seed,
        "preview_score": round(sample_size * threshold * scale, 3),
    }

    return {
        "ok": True,
        "image_base64": None,
        "stats": stats,
        "warnings": [],
    }