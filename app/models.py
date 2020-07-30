from pathlib import Path
from typing import Dict, Iterator, List, Optional

from datafiles import datafile, field
from sanic import Sanic

from .types import Dimensions, Point


@datafile
class Text:

    color: str = "white"

    anchor_x: float = 0.1
    anchor_y: float = 0.1

    angle: float = 0

    scale_x: float = 0.8
    scale_y: float = 0.2

    def get_anchor(self, size: Dimensions) -> Point:
        return int(size[0] * self.anchor_x), int(size[1] * self.anchor_y)


@datafile("../templates/{self.key}/config.yml")
class Template:

    key: str
    name: str = ""
    source: Optional[str] = None
    text: List[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.1, anchor_y=0.9)]
    )
    styles: List[str] = field(default_factory=lambda: ["default"])
    sample: List[str] = field(default_factory=lambda: ["YOUR TEXT", "GOES HERE"])

    @property
    def valid(self) -> bool:
        return bool(self.name and not self.name.startswith("<"))

    @property
    def background_image_path(self) -> Path:
        for ext in ["png", "jpg"]:
            path = self.datafile.path.parent / f"default.{ext}"
            if path.exists():
                return path
        raise ValueError(f"No background image for template: {self}")

    def jsonify(self, app: Sanic) -> Dict:
        return {
            "name": self.name,
            "styles": [s for s in self.styles if s != "default"],
            "blank": app.url_for("images.blank", key=self.key, _external=True),
            "sample": self.build_sample_url(app),
            "source": self.source,
            "_self": app.url_for("templates.detail", key=self.key, _external=True),
        }

    def build_sample_url(self, app: Sanic) -> str:
        return app.url_for(
            "images.text",
            key=self.key,
            lines="/".join(self._encode(*self.sample)),
            _external=True,
        )

    @staticmethod
    def _encode(*lines: str) -> Iterator[str]:
        for line in lines:
            if line:
                yield line.lower().replace(" ", "_").replace("?", "~q")
            else:
                yield "_"