from pathlib import Path
from subprocess import check_output
from xml.etree import ElementTree

SVG = "http://www.w3.org/2000/svg"
CHART_URL = "https://ghchart.rshah.org/ec4899/sampurnachandra97-max"

chart = ElementTree.fromstring(check_output(["curl", "-fsSL", "--max-time", "30", CHART_URL]))

days = chart.findall(f"{{{SVG}}}rect[@data-score][@data-date]")
if chart.tag != f"{{{SVG}}}svg" or not 350 <= len(days) <= 380:
    raise ValueError("Unexpected contribution calendar format")

for day in days:
    color = "#000000" if int(day.attrib["data-score"]) == 0 else "#ec4899"
    day.set("style", f"fill:{color};shape-rendering:crispedges;")

ElementTree.register_namespace("", SVG)
Path("contribution-calendar.svg").write_bytes(
    ElementTree.tostring(chart, encoding="utf-8") + b"\n"
)
