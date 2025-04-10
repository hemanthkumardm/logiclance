import os
import stat
import shutil
from pathlib import Path

def create_cli_symlink():
    home = Path.home()
    bin_dir = home / "bin"
    bin_dir.mkdir(exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    cli_script = repo_root / "flow_gui" / "main.py"
    configs_dir = repo_root / "flow_gui" / "configs"
    symlink_path = bin_dir / "logiclance"

    # Find a launch.sh script if present
    launch_scripts = list(configs_dir.glob("*.sh"))
    launch_script = launch_scripts[0] if launch_scripts else None

    if not cli_script.exists():
        print(f"CLI script not found at {cli_script}")
        return

    python_exec = shutil.which("python3")
    if not python_exec:
        print("python3 not found in PATH")
        return

    # Write wrapper script
    with open(symlink_path, "w") as f:
        f.write("#!/bin/bash\n")
        if launch_script:
            f.write(f"source \"{launch_script}\"\n")
        f.write(f"\"{python_exec}\" \"{cli_script}\" \"$@\"\n")

    symlink_path.chmod(symlink_path.stat().st_mode | stat.S_IEXEC)
    print(f"CLI command 'logiclance' created at {symlink_path}")

    # Update PATH in ~/.bashrc (only once!)
    bashrc = home / ".bashrc"
    path_marker = "# >>> Logic Lance CLI >>>"
    path_line = f'export PATH="$HOME/bin:$PATH"  # added by Logic Lance\n'

    if bashrc.exists():
        content = bashrc.read_text(encoding="utf-8")
        if path_marker not in content:
            with open(bashrc, "a") as f:
                f.write(f"\n{path_marker}\n{path_line}# <<< Logic Lance CLI <<<\n")
            print("Added ~/bin to PATH in ~/.bashrc")
        else:
            print("PATH entry already exists in ~/.bashrc")
    else:
        bashrc.write_text(f"{path_marker}\n{path_line}# <<< Logic Lance CLI <<<\n")
        print("Created ~/.bashrc and added PATH")

    print("Please run: source ~/.bashrc or restart your terminal")

if __name__ == "__main__":
    create_cli_symlink()
