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
        # 按顺序尝试，命中第一个存在的目录即使用
        "skills_subdirs": ["skills"],
    },
    {
        "name": "Jeffallan-claude-skills",
        "url": "https://github.com/Jeffallan/claude-skills",
        # 该仓库把 skills 放在 plugin/ 下，不写死单一路径以便兼容后续调整
        "skills_subdirs": ["plugin/skills", "skills", ".claude/skills"],
    },
    {
        "name": "zhaoxuya520-reverse-skill",
        "url": "https://github.com/zhaoxuya520/reverse-skill",
        "skills_subdirs": ["skills"],
    },
]

# 自动探测 skills 目录时跳过这些目录
SKIP_DIR_NAMES = {".git", "node_modules", "dist", "build", "__pycache__", ".venv"}

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


def reset_log(header: str) -> None:
    """清空日志文件，只保留本次运行的内容（每次运行前调用一次）。"""
    print(header)
    LOG_FILE.write_text(header + "\n", encoding="utf-8")


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


def files_equal(old: Path, new: Path) -> bool:
    """判断两个文件内容是否一致；文本文件忽略换行符差异（CRLF/LF）。"""
    if filecmp.cmp(old, new, shallow=False):
        return True
    old_text = read_text_safe(old)
    new_text = read_text_safe(new)
    if old_text is None or new_text is None:  # 二进制或非 UTF-8，只能按字节比较
        return False
    return old_text.replace("\r\n", "\n") == new_text.replace("\r\n", "\n")


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
        if not files_equal(old_files[rel], new_files[rel]):
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


def find_skills_dir(clone_dir: Path, candidates: list[str]) -> tuple[Path, str | None]:
    """定位仓库中的 skills 目录。

    先按配置的候选路径依次尝试；全部未命中时在仓库内自动探测名为 skills 的目录
    （取层级最浅的一个）。返回 (目录绝对路径, 命中的候选路径)；自动探测时第二项为 None。
    """
    for cand in candidates:
        path = clone_dir / cand
        if path.is_dir():
            return path, cand

    found: list[Path] = []
    for path in clone_dir.rglob("skills"):
        if not path.is_dir():
            continue
        rel_parts = path.relative_to(clone_dir).parts
        if any(part in SKIP_DIR_NAMES for part in rel_parts):
            continue
        found.append(path)

    if found:
        found.sort(key=lambda p: (len(p.relative_to(clone_dir).parts), p.as_posix()))
        return found[0], None

    top_level = sorted(
        f"{p.name}/" if p.is_dir() else p.name
        for p in clone_dir.iterdir()
        if p.name != ".git"
    )
    raise FileNotFoundError(
        f"仓库中未找到 skills 目录（已尝试: {', '.join(candidates)}）；"
        f"仓库顶层内容: {', '.join(top_level) or '(空)'}"
    )


def prepare_new_skills(clone_dir: Path, candidates: list[str]) -> tuple[Path, str]:
    """在临时克隆目录中定位 skills 目录，只保留其中的子文件夹（单文件删除）。

    返回 (暂存目录, 定位到的 skills 目录描述)。
    """
    skills_dir, matched = find_skills_dir(clone_dir, candidates)

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

    if not any(staged.iterdir()):
        raise FileNotFoundError(f"目录 '{skills_dir}' 中没有任何技能内容: {clone_dir}")

    located = matched if matched else "自动探测"
    return staged, f"{skills_dir.relative_to(clone_dir).as_posix()}（{located}）"


def sync_tree(src: Path, dst: Path) -> tuple[int, int, int]:
    """把 src 同步到 dst，只改动有差异的文件，避免整目录删除重建。

    返回 (新增, 更新, 删除) 的文件数量。
    """
    src_files = collect_files(src)
    dst_files = collect_files(dst) if dst.exists() else {}

    removed = sorted(set(dst_files) - set(src_files))
    added = sorted(set(src_files) - set(dst_files))
    updated = [
        rel for rel in sorted(set(src_files) & set(dst_files))
        if not files_equal(dst_files[rel], src_files[rel])
    ]

    for rel in removed:
        dst_files[rel].unlink()
    # 清理因删除文件而变空的目录（浅层优先删除，因此按层级倒序处理）
    if dst.exists():
        dirs = sorted(
            (p for p in dst.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        )
        for d in dirs:
            if not any(d.iterdir()):
                d.rmdir()

    for rel in list(added) + updated:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_files[rel], target)

    return len(added), len(updated), len(removed)


def update_repo(repo: dict) -> bool:
    """处理单个仓库。返回 True 表示成功。"""
    name = repo["name"]
    url = repo["url"]
    candidates = repo.get("skills_subdirs") or [repo.get("skills_subdir", "skills")]
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
            staged, located = prepare_new_skills(clone_dir, candidates)
        except FileNotFoundError as e:
            log(f"  [错误] {e}")
            return False

        log(f"  已定位 skills 目录: {located}")

        has_local = local_dir.exists() and any(local_dir.iterdir())
        log(f"  Diff 结果（本地 <-> 远程）:")
        for line in diff_directories(local_dir if has_local else None, staged):
            log(line)

        # 同步本地内容（只改动有差异的文件，不做整目录删除重建）
        if has_local:
            added, updated, removed = sync_tree(staged, local_dir)
            if added or updated or removed:
                log(
                    f"  已同步本地内容: 新增 {added} / 更新 {updated} / "
                    f"删除 {removed} -> {local_dir}"
                )
            else:
                log(f"  本地内容已是最新，无需改动: {local_dir}")
        else:
            shutil.copytree(staged, local_dir, dirs_exist_ok=True)
            log(f"  已写入本地内容: {local_dir}")
    return True


def main() -> int:
    header = (
        f"\n{'#' * 60}\n"
        f"# skills-updater 运行时间: "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'#' * 60}"
    )
    # 本次运行的日志覆盖上一次，避免日志文件无限增长
    reset_log(header)

    failed = [r["name"] for r in REPOS if not update_repo(r)]
    if failed:
        log(f"\n以下仓库更新失败: {', '.join(failed)}")
        return 1
    log("\n全部仓库更新完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
