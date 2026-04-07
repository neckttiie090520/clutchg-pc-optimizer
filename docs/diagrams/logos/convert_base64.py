import base64
import os

logo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
results = {}

for f in os.listdir(logo_dir):
    if f.endswith(".svg"):
        name = f.replace(".svg", "")
        filepath = os.path.join(logo_dir, f)
        with open(filepath, "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("ascii")
        results[name] = f"data:image/svg+xml;base64,{b64}"
        print(f"{name}: {len(b64)} chars base64")

# Write output file
out_path = os.path.join(logo_dir, "logo_base64.txt")
with open(out_path, "w") as fh:
    for name, uri in sorted(results.items()):
        fh.write(f"=== {name} ===\n{uri}\n\n")

print(f"\nWrote {len(results)} logos to logo_base64.txt")
