#!/usr/bin/env python3
"""Research orchestrator — clone repos, run analysis, generate reports."""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import yaml
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table

console = Console()
REPO_DIR = Path("tmp")
REPORTS_DIR = Path("docs/research")
STATUS_FILE = Path("tmp/.research_status.json")


def load_config(config_path):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    repos = cfg.get("repos", [])
    if not repos:
        console.print("[red]No repos defined in config[/red]")
        sys.exit(1)
    return cfg


def load_status():
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {}


def save_status(status):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def clone_repo(url, name, target):
    if target.exists():
        console.print(f"  [yellow]→ Already exists, pulling[/yellow]")
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=target,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            console.print(f"  [red]  Pull failed: {result.stderr.strip()}[/red]")
        return
    console.print(f"  [cyan]→ Cloning[/cyan]")
    result = subprocess.run(
        ["git", "clone", url, str(target)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        console.print(f"  [red]  Clone failed: {result.stderr.strip()}[/red]")
        raise RuntimeError(f"Clone failed for {name}")


def create_zip(repo_dir, output_path):
    output_path = Path(output_path)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(repo_dir):
            # skip .git
            if ".git" in Path(root).parts:
                continue
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(repo_dir.parent)
                zf.write(fp, arcname)
    return output_path


def run_analysis_commands(repo_name, commands, report_dir, repo_dir):
    for cmd_template in commands:
        cmd = cmd_template.format(
            repo_dir=str(repo_dir),
            report_dir=str(report_dir),
            repo_name=repo_name
        )
        console.print(f"  [dim]→ Running: {cmd}[/dim]")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        log_path = report_dir / f"cmd_{len(os.listdir(report_dir))}.log"
        with open(log_path, "w") as f:
            f.write(f"$ {cmd}\n\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        if result.returncode != 0:
            console.print(f"  [red]  Exit code {result.returncode}[/red]")


def write_report_intro(report_dir, repo_name, repo_url, prompt, repo_dir):
    """Write the initial markdown report with repo info and prompt."""
    report_path = report_dir / "README.md"

    # gather basic repo stats
    git_log = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        cwd=repo_dir, capture_output=True, text=True
    ).stdout

    file_count = 0
    lang_stats = {}
    for root, _dirs, files in os.walk(repo_dir):
        if ".git" in Path(root).parts:
            continue
        file_count += len(files)
        for f in files:
            ext = Path(f).suffix
            lang_stats[ext] = lang_stats.get(ext, 0) + 1

    lines = [
        f"# Research: {repo_name}",
        f"",
        f"- **URL:** {repo_url}",
        f"- **Cloned:** {datetime.now().isoformat()}",
        f"- **Files:** {file_count}",
        f"- **Top extensions:** {dict(sorted(lang_stats.items(), key=lambda x: -x[1])[:10])}",
        f"",
        f"## Analysis Prompt",
        f"",
        f"```",
        prompt.strip(),
        f"```",
        f"",
        f"## Recent Commits",
        f"",
        f"```",
        git_log.strip() if git_log.strip() else "(no commits)",
        f"```",
        f"",
        f"## Directory Structure",
        f"",
        f"```",
    ]

    # tree output
    tree = subprocess.run(
        ["tree", "-L", "2", "--dirsfirst", "--noreport", str(repo_dir)],
        capture_output=True, text=True
    ).stdout
    # filter out .git
    tree_lines = [l for l in tree.split("\n") if ".git" not in l and "__pycache__" not in l]
    lines.append("\n".join(tree_lines[:80]))
    lines.append("```")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("_Add analysis notes below..._")
    lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path


@click.command()
@click.option("--config", "-c", default="src/research_config.yaml",
              help="Path to config YAML file", show_default=True)
@click.option("--repos", "-r", default=None,
              help="Comma-separated list of repo names to process (all if omitted)")
@click.option("--skip-clone", is_flag=True, help="Skip clone step")
@click.option("--skip-zip", is_flag=True, help="Skip zip creation")
@click.option("--skip-commands", is_flag=True, help="Skip analysis commands")
@click.option("--status", is_flag=True, help="Show status table and exit")
def main(config, repos, skip_clone, skip_zip, skip_commands, status):
    """Research orchestration: clone repos, run analysis, generate reports."""

    REPO_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    cfg = load_config(config)
    global_prompt = cfg.get("prompt", "Analyze this codebase.")

    all_repos = cfg.get("repos", [])
    status_data = load_status()

    # filter by --repos if provided
    if repos:
        names = [n.strip() for n in repos.split(",")]
        filtered = [r for r in all_repos if r["name"] in names]
        missing = set(names) - {r["name"] for r in filtered}
        if missing:
            console.print(f"[yellow]Unknown repos: {missing}[/yellow]")
        all_repos = filtered

    # status-only mode
    if status:
        show_status(all_repos, status_data)
        return

    # summary table before starting
    table = Table(title="Research Plan")
    table.add_column("Repo", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Zip", style="yellow")
    table.add_column("Reports", style="blue")
    for repo in all_repos:
        s = status_data.get(repo["name"], {})
        cloned = "✅" if s.get("cloned") else "⬜"
        zipped = "✅" if s.get("zipped") else "⬜"
        reported = "✅" if s.get("reported") else "⬜"
        table.add_row(repo["name"], cloned, zipped, reported)
    console.print(table)

    if not click.confirm("Proceed with research?"):
        return

    # Process each repo
    errors = []
    for repo in all_repos:
        name = repo["name"]
        url = repo["url"]
        create_zip_flag = repo.get("create_zip", False)
        commands = repo.get("analysis_commands", [])
        repo_prompt = repo.get("prompt", global_prompt)
        target = REPO_DIR / name

        console.print(f"\n[bold]=== {name} ===[/bold]")

        # 1. Clone
        if not skip_clone:
            try:
                clone_repo(url, name, target)
                status_data.setdefault(name, {})["cloned"] = True
                save_status(status_data)
            except RuntimeError as e:
                console.print(f"[red]  ERROR: {e}[/red]")
                errors.append(name)
                continue

        # 2. Create report dir and intro
        report_dir = REPORTS_DIR / name
        report_dir.mkdir(parents=True, exist_ok=True)
        write_report_intro(report_dir, name, url, repo_prompt, target)
        status_data.setdefault(name, {})["reported"] = True
        save_status(status_data)

        # 3. Run analysis commands
        if not skip_commands and commands:
            run_analysis_commands(name, commands, report_dir, target)

        # 4. Zip
        if not skip_zip and create_zip_flag:
            zip_path = REPO_DIR / f"{name}.zip"
            create_zip(target, zip_path)
            console.print(f"  [green]→ Zip: {zip_path}[/green]")
            status_data.setdefault(name, {})["zipped"] = True
            save_status(status_data)

    # Final summary
    console.print("\n[bold]Done.[/bold]")
    if errors:
        console.print(f"[red]Errors: {errors}[/red]")


def show_status(all_repos, status_data):
    table = Table(title="Research Status")
    table.add_column("Repo", style="cyan")
    table.add_column("Cloned", style="green")
    table.add_column("Zipped", style="yellow")
    table.add_column("Reported", style="blue")
    for repo in all_repos:
        s = status_data.get(repo["name"], {})
        cloned = "✅" if s.get("cloned") else "⬜"
        zipped = "✅" if s.get("zipped") else "⬜"
        reported = "✅" if s.get("reported") else "⬜"
        table.add_row(repo["name"], cloned, zipped, reported)
    console.print(table)


if __name__ == "__main__":
    main()
