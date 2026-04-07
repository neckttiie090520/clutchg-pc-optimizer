import base64
import os

logo_dir = r"C:\Users\nextzus\Documents\thesis\bat\docs\diagrams\logos"
logos = {}

for f in os.listdir(logo_dir):
    if f.endswith(".svg"):
        name = f.replace(".svg", "")
        with open(os.path.join(logo_dir, f), "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("ascii")
        logos[name] = f"data:image/svg+xml;base64,{b64}"

# Print length of each
for name, uri in sorted(logos.items()):
    print(f"{name}: total_uri_len={len(uri)}")

# Now generate the image cells for draw.io
# Card positions and logo mapping:
cards = [
    # (cell_id, x, y, width, height, logo_name)
    ("t_python", 65, 150, 130, 65, "python"),
    ("t_ctk", 210, 150, 140, 65, "python"),  # CustomTkinter = Python lib
    ("t_psutil", 65, 310, 120, 65, "python"),  # psutil = Python lib
    ("t_pywin32", 450, 310, 120, 65, "windows"),  # pywin32 = Windows API
    ("t_bat", 65, 468, 130, 65, "windows"),  # CMD = Windows
    ("t_ps", 210, 468, 130, 65, "powershell"),
    ("t_registry", 65, 628, 120, 65, "windows"),
    ("t_restore", 65, 788, 140, 65, "windows"),  # System Restore = Windows
    ("t_rollback", 750, 788, 140, 65, "windows"),  # Rollback = Windows mechanism
    ("t_pytest", 190, 943, 130, 65, "pytest"),
    ("t_git", 668, 943, 120, 65, "git"),
]

# Generate mxCell XML for each logo image
# Place icon at top-left of card with padding
icon_size = 22
padding = 6

xml_cells = []
for cell_id, cx, cy, cw, ch, logo_name in cards:
    icon_id = f"icon_{cell_id}"
    ix = cx + padding
    iy = cy + padding
    uri = logos[logo_name]
    xml = f'        <mxCell id="{icon_id}" value="" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=none;imageBackgroundColor=none;imageAlign=left;imageBorder=none;image={uri};imageWidth={icon_size};imageHeight={icon_size};" vertex="1" parent="1">\n'
    xml += f'          <mxGeometry x="{ix}" y="{iy}" width="{icon_size}" height="{icon_size}" as="geometry"/>\n'
    xml += f"        </mxCell>"
    xml_cells.append(xml)

# Write the XML snippet
out = os.path.join(logo_dir, "icon_cells.xml")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n\n".join(xml_cells))

print(f"\nWrote {len(xml_cells)} icon cells to icon_cells.xml")
