import requests, sys

path = sys.argv[1]
fname = path.split("\\")[-1]

with open(path, "rb") as f:
    files = {"file": (fname, f, "application/octet-stream")}
    r = requests.post("http://localhost:8000/candidates/upload", files=files, timeout=120)

if r.status_code == 201:
    d = r.json()
    skills = [s["name"] for s in d.get("skills", [])]
    print(f"OK: {d['full_name']} | {len(skills)} skills | {d['years_experience']} yrs")
    print("Skills:", skills[:20])
elif r.status_code == 409:
    print(f"SKIP (duplicate): {r.json().get('detail')}")
else:
    print(f"ERROR {r.status_code}: {r.text[:400]}")
