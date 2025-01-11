from typing import Optional

def to_svg(
    text: str,
    font_size: Optional[int] = None,
    font_family: Optional[str] = None,
    fill_color: Optional[str] = None,
    background: Optional[str] = None,
    stroke_color: Optional[str] = None,
    stroke_width: Optional[float] = None,
    scale: Optional[float] = None,
    include_backdrop: bool = False,
    include_styles: bool = True,
    include_defs: bool = True,
) -> str:
    ...
