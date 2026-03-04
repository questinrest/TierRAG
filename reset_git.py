import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    print(f"Return code: {result.returncode}\n")
    return result.returncode == 0

commands = [
    "git checkout --orphan temp_branch",
    "git add -A",
    "git commit -m \"Initial commit (history cleared)\"",
    "git branch -D main",
    "git branch -m main",
    "git push -f origin main"
]

print("Starting Git history reset...\n")
for c in commands:
    success = run_cmd(c)
    if not success and c != "git branch -D main": # Allow branch delete to fail if main doesn't exist
        print("Command failed. Stopping.")
        break
print("Finished.")
