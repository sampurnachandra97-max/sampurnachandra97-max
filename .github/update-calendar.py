from pathlib import Path
import re
from subprocess import check_output
from xml.etree import ElementTree

SVG = "http://www.w3.org/2000/svg"
CHART_URL = "https://ghchart.rshah.org/ec4899/sampurnachandra97-max"

chart = ElementTree.fromstring(check_output(["curl", "-fsSL", "--max-time", "30", CHART_URL]))

days = chart.findall(f"{{{SVG}}}rect[@data-score][@data-date]")
if chart.tag != f"{{{SVG}}}svg" or not 350 <= len(days) <= 380:
    raise ValueError("Unexpected contribution calendar format")

profile_calendar = check_output([
    "curl", "-fsSL", "--max-time", "30",
    "https://github.com/users/sampurnachandra97-max/contributions",
]).decode("utf-8")
counts_by_id = {}
for attributes, label in re.findall(r"<tool-tip\b([^>]+)>([^<]+)</tool-tip>", profile_calendar):
    target = re.search(r'\bfor="([^"]+)"', attributes)
    count = re.match(r"\s*(No|[\d,]+) contributions? on ", label)
    if target and count:
        value = count.group(1)
        counts_by_id[target.group(1)] = 0 if value == "No" else int(value.replace(",", ""))

counts_by_date = {}
for attributes in re.findall(r"<td\b([^>]+)>", profile_calendar):
    date = re.search(r'\bdata-date="([^"]+)"', attributes)
    cell = re.search(r'\bid="([^"]+)"', attributes)
    if date and cell and cell.group(1) in counts_by_id:
        counts_by_date[date.group(1)] = counts_by_id[cell.group(1)]
if len(counts_by_date) < 350:
    raise ValueError("Could not read GitHub's daily contribution counts")

palette = ("#000000", "#fbcfe8", "#f472b6", "#ec4899", "#be185d")
for day in days:
    date = day.attrib["data-date"]
    if date not in counts_by_date and day.attrib["data-score"] != "0":
        raise ValueError(f"No GitHub contribution count for {date}")
    count = counts_by_date.get(date, 0)
    day.set("data-count", str(count))
    color = palette[min(count, len(palette) - 1)]
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
Path("contribution-calendar-counts.svg").write_bytes(
    ElementTree.tostring(chart, encoding="utf-8") + b"\n"
)
