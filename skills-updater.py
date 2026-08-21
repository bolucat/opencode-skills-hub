import datetime
import difflib
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# 配置：需要更新的仓库列表，未来新增仓库直接在下面追加即可
# ---------------------------------------------------------------------------
REPOS = [
    {
        "name": "anthropics-skills",
        "url": "https://github.com/anthropics/skills",
        "skills_subdir": "skills",
    },
    {
        "name": "Jeffallan-claude-skills",
        "url": "https://github.com/Jeffallan/claude-skills",
        "skills_subdir": "skills",
    },
    {
        "name": "zhaoxuya520-reverse-skill",
        "url": "https://github.com/zhaoxuya520/reverse-skill",
        "skills_subdir": "skills",
    },
]

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "updater.log"
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".sh",
    ".js", ".ts", ".html", ".css", ".xml", ".csv", ".ini", ".cfg",
}


def log(msg: str) -> None:
    print(msg)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def run_git(args: list[str], cwd: Path | None = None) -> None:
    cmd = ["git"] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"git 命令失败: {' '.join(cmd)}\n{result.stderr.strip()}"
        )


def collect_files(root: Path) -> dict[str, Path]:
    """返回 {相对路径: 文件绝对路径}"""
    return {
        p.relative_to(root).as_posix(): p
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def diff_directories(old_root: Path | None, new_root: Path) -> list[str]:
    """比较新旧两个目录，返回人类可读的差异行列表。old_root 为 None 表示全新安装。"""
    lines: list[str] = []
    old_files = collect_files(old_root) if old_root and old_root.exists() else {}
    new_files = collect_files(new_root)

    removed = sorted(set(old_files) - set(new_files))
    added = sorted(set(new_files) - set(old_files))
    common = sorted(set(old_files) & set(new_files))

    if removed:
        lines.append("  [删除的文件]")
        lines.extend(f"    - {p}" for p in removed)
    if added:
        lines.append("  [新增的文件]")
        lines.extend(f"    + {p}" for p in added)

    modified = []
    for rel in common:
        if not filecmp.cmp(old_files[rel], new_files[rel], shallow=False):
            modified.append(rel)
    if modified:
        lines.append("  [修改的文件]")

    for rel in modified:
        lines.append(f"    ~ {rel}")
        old_text = read_text_safe(old_files[rel])
        new_text = read_text_safe(new_files[rel])
        if (
            old_text is not None
            and new_text is not None
            and new_files[rel].suffix.lower() in TEXT_SUFFIXES
        ):
            diff = difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"a/{rel}",
                tofile=f"b/{rel}",
            )
            lines.extend("    " + l.rstrip("\n") for l in diff)
        else:
            lines.append("      (二进制文件或无法解码，仅标记为已修改)")

    if not lines:
        lines.append("  无变化")
    return lines


def prepare_new_skills(clone_dir: Path, skills_subdir: str) -> Path:
    """在临时克隆目录中定位 skills 目录，只保留其中的子文件夹（单文件删除）。"""
    skills_dir = clone_dir / skills_subdir
    if not skills_dir.is_dir():
        raise FileNotFoundError(
            f"仓库中未找到目录 '{skills_subdir}': {clone_dir}"
        )
    for entry in list(skills_dir.iterdir()):
        if entry.is_file():
            entry.unlink()
        elif entry.is_dir() and not any(entry.iterdir()):
            entry.rmdir()
    # 把 skills 目录内容挪到一个干净的暂存根目录，方便整体替换
    staged = clone_dir / "_staged"
    staged.mkdir()
    for entry in skills_dir.iterdir():
        shutil.move(str(entry), str(staged / entry.name))
    return staged


def update_repo(repo: dict) -> bool:
    """处理单个仓库。返回 True 表示成功。"""
    name = repo["name"]
    url = repo["url"]
    skills_subdir = repo.get("skills_subdir", "skills")
    local_dir = BASE_DIR / name

    log(f"\n{'=' * 60}")
    log(f"[{name}] 开始更新 ({url})")

    with tempfile.TemporaryDirectory(prefix=f"skills-updater-{name}-") as tmp:
        tmp_path = Path(tmp)
        clone_dir = tmp_path / "clone"
        try:
            run_git(["clone", "--depth=1", url, str(clone_dir)])
        except RuntimeError as e:
            log(f"  [错误] 克隆失败:\n{e}")
            return False

        try:
            staged = prepare_new_skills(clone_dir, skills_subdir)
        except FileNotFoundError as e:
            log(f"  [错误] {e}")
            return False

        has_local = local_dir.exists() and any(local_dir.iterdir())
        log(f"  Diff 结果（本地 <-> 远程）:")
        for line in diff_directories(local_dir if has_local else None, staged):
            log(line)

        # 替换本地内容
        if local_dir.exists():
            shutil.rmtree(local_dir)
        shutil.copytree(staged, local_dir)
        log(f"  已替换本地内容: {local_dir}")
    return True


def main() -> int:
    header = (
        f"\n{'#' * 60}\n"
        f"# skills-updater 运行时间: "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'#' * 60}"
    )
    log(header)

    failed = [r["name"] for r in REPOS if not update_repo(r)]
    if failed:
        log(f"\n以下仓库更新失败: {', '.join(failed)}")
        return 1
    log("\n全部仓库更新完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
