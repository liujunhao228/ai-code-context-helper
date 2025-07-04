import os
import shutil
import subprocess
import sys
from pathlib import Path
import zipfile
import re

def run(cmd, check=True, shell=True):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if check and result.returncode != 0:
        print(f"ERROR: Command failed: {cmd}")
        sys.exit(1)

def check_tool(tool):
    result = shutil.which(tool)
    if not result:
        print(f"ERROR: {tool} not found. Please install it first.")
        sys.exit(1)

def main():
    # 1. Check dependencies
    check_tool("pipx")
    check_tool("poetry")
    check_tool("gh")

    # 2. Install dependencies
    run("poetry install")

    # 3. Clean previous build
    if Path("build").exists():
        shutil.rmtree("build")

    # 4. Build with cx_Freeze
    run("poetry run cxfreeze build")

    # 5. Find build output directory
    build_dir = Path("build")
    exe_dirs = [d for d in build_dir.iterdir() if d.is_dir() and d.name.startswith("exe.win-")]
    if not exe_dirs:
        print("ERROR: No exe.win-* directory found in build.")
        sys.exit(1)
    srcdir = exe_dirs[0]
    print(f"Found build output directory: {srcdir}")

    # 6. Prepare new directory name
    basename = "ai-code-context-helper-master"
    if srcdir.name.startswith("exe.win-"):
        platform_str = srcdir.name[len("exe.win-"):]  # e.g. 'amd64-3.13' or 'amd64'
        platform_str = platform_str.split("-")[0] if "-" in platform_str else platform_str
        verstr = f"win-{platform_str}"
    else:
        verstr = srcdir.name[len("exe."):]  # fallback
    version = input("Please enter release version (e.g. v1.0.0): ").strip()
    if not version:
        print("ERROR: No version entered.")
        sys.exit(1)
    # 读取CHANGELOG.md中与当前version匹配的最新一条
    changelog_path = Path("CHANGELOG.md")
    if changelog_path.exists():
        with changelog_path.open("r", encoding="utf-8") as f:
            changelog = f.read()
        def extract_latest_changelog(changelog, version):
            pattern = re.compile(rf"##\\s*{re.escape(version)}[\\s\\S]*?(?=^##\\s|\Z)", re.MULTILINE)
            match = pattern.search(changelog)
            if match:
                return match.group(0)
            return f"Auto release {version}"
        release_note = extract_latest_changelog(changelog, version)
    else:
        release_note = f"Auto release {version}"
    newdir = build_dir / f"{basename}-{verstr}-{version}"
    print(f"New directory name will be: {newdir}")

    # 7. Copy and rename directory
    if newdir.exists():
        shutil.rmtree(newdir)
    shutil.copytree(srcdir, newdir)

    # 8. Zip the directory
    zip_path = Path(f"{newdir}.zip")
    print(f"Zipping directory to {zip_path} ...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(newdir):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(newdir.parent))

    # 10. Create GitHub release and upload zip
    print("Creating GitHub release...")
    run(f'gh release create {version} "{zip_path}" --title "{version}" --notes """{release_note}"""')

    # 11. Clean up
    shutil.rmtree(newdir)
    zip_path.unlink()
    print("Release completed successfully!")

if __name__ == "__main__":
    main() 