from pathlib import Path

import yaml

from demo_reel.config import DemoReelConfig, load_config


def test_load_config_resolves_paths(tmp_path: Path) -> None:
    cfg_file = tmp_path / "demo-reel.yaml"
    cfg_file.write_text(
        yaml.dump(
            {
                "project_name": "Test",
                "narration": {"file": "narration.txt"},
                "output": {"dir": "out", "filename": "test.mp4"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "narration.txt").write_text("hello", encoding="utf-8")
    config = load_config(cfg_file)
    assert config.project_name == "Test"
    assert config.narration_path() == tmp_path / "narration.txt"
    assert config.output_mp4() == tmp_path / "out" / "test.mp4"


def test_demo_url_and_health() -> None:
    config = DemoReelConfig()
    config._root = Path("/repo")  # type: ignore[attr-defined]
    config.server.port = 9000
    assert "9000" in config.health_url()
    assert "duration=45.00" in config.demo_url(45.0)
