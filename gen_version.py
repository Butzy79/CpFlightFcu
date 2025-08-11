import re
import os

def get_latest_release_version(changelog_path='CHANGELOG.md'):
    print(f"Reading changelog from: {os.path.abspath(changelog_path)}")
    with open(changelog_path, 'r') as file:
        content = file.read()
    versions = re.findall(r'\[\d+\.\d+\.\d+\]', content)
    if not versions:
        return "0.0.0"
    return versions[0].strip('[]')

version = get_latest_release_version()

os.makedirs('lib', exist_ok=True)

output_path = 'lib/version.py'
print(f"Writing version to: {os.path.abspath(output_path)}")

with open(output_path, 'w') as f:
    f.write(f'__version__ = "{version}"\n')

print("Done!")
