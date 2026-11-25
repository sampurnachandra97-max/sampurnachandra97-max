from pathlib import Path
from subprocess import check_output
from xml.etree import ElementTree

SVG = "http://www.w3.org/2000/svg"
CHART_URL = "https://ghchart.rshah.org/ec4899/sampurnachandra97-max"

chart = ElementTree.fromstring(check_output(["curl", "-fsSL", "--max-time", "30", CHART_URL]))

days = chart.findall(f"{{{SVG}}}rect[@data-score][@data-date]")
if chart.tag != f"{{{SVG}}}svg" or not 350 <= len(days) <= 380:
    raise ValueError("Unexpected contribution calendar format")

# Keep GitHub-style intensity levels, using pink for active days.
palette = ("#000000", "#fbcfe8", "#f472b6", "#ec4899", "#be185d")
for day in days:
    score = int(day.attrib["data-score"])
    level = min(score, len(palette) - 1)
    color = palette[level]
    day.set("style", f"fill:{color};shape-rendering:crispedges;")

namespace = f"{{{SVG}}}"
chart.set("height", str(int(chart.attrib["height"]) + 24))
legend = ElementTree.SubElement(chart, namespace + "g", {"aria-label": "Contributions per day"})
for index, (color, label) in enumerate(zip(palette, ("0", "1", "2", "3", "4+"))):
    x = 458 + 39 * index
    swatch = ElementTree.SubElement(
        legend, namespace + "rect",
        {"x": str(x), "y": "109", "width": "10", "height": "10", "rx": "2",
         "fill": color, "stroke": "#788391", "stroke-width": "0.5"},
    )
    ElementTree.SubElement(swatch, namespace + "title").text = f"{label} contributions"
    ElementTree.SubElement(
        legend, namespace + "text",
        {"x": str(x + 14), "y": "118", "fill": "#788391",
         "font-size": "10", "font-family": "system-ui,sans-serif"},
    ).text = label

ElementTree.register_namespace("", SVG)
Path("contribution-calendar-pink.svg").write_bytes(
    ElementTree.tostring(chart, encoding="utf-8") + b"\n"
)
