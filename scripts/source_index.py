"""Regenerate a portable relative source index and an optional source archive."""
import argparse
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ['README.md', 'SOURCE_INDEX.md', '.env.example', '.gitignore', '.gitattributes', 'run.py', 'start.ps1',
              'requirements.txt', 'requirements-dev.txt', 'requirements-lock.txt',
              'pytest.ini', 'Dockerfile', 'compose.yaml', '.dockerignore']
GROUPS = [('说明、配置与启动', None), ('前端', 'dist'), ('后端', 'backend'), ('测试', 'tests'),
          ('评估数据与协议', 'evals'), ('运行与实验脚本', 'scripts'), ('架构与修改说明', 'docs'),
          ('示例 PDF', 'samples'), ('持续集成', '.github')]


def source_files():
    result = {}
    for title, folder in GROUPS:
        files = []
        if folder is None:
            files = [Path(name) for name in ROOT_FILES if (ROOT / name).is_file()]
        else:
            for directory, dirs, names in os.walk(ROOT / folder):
                dirs[:] = sorted(name for name in dirs if name not in ('__pycache__', 'reports'))
                for name in sorted(names):
                    if Path(name).suffix not in ('.pyc', '.log'):
                        files.append((Path(directory) / name).relative_to(ROOT))
        result[title] = sorted(files)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='store_true')
    args = parser.parse_args()
    groups = source_files()
    reports = sorted(path.relative_to(ROOT) for path in (ROOT / 'reports').rglob('*')
                     if path.is_file() and path.suffix in ('.md', '.json') and
                     not any(part.startswith('store-benchmark-') for part in path.parts))
    lines = ['# Knowbase 源码目录', '',
             '所有链接相对于项目根目录，复制、克隆或解压到其他位置后仍可使用。', '',
             '目录由 `python -m scripts.source_index` 从当前文件生成；`dist/` 就是可直接修改的 HTML、JavaScript、CSS 源文件，无需额外构建。', '',
             '需要完整压缩包时运行 `python -m scripts.source_index --archive`，输出 `exports/knowbase-source-latest.zip`。', '']
    files = []
    for title, group in groups.items():
        lines += [f'## {title}', '']
        for file in group:
            name = file.as_posix()
            lines.append(f'- [{name}]({name})')
            files.append(file)
        lines.append('')
    lines += ['## 实际运行报告', '', '报告包含运行时间与验证范围，blocked/skipped 表示尚未实测或未执行。', '']
    for report in reports:
        lines.append(f'- [{report.as_posix()}]({report.as_posix()})')
    lines += ['', '## 运行数据', '',
              '`data/`、`pgdata/`、`.venv/`、`.git/`、缓存、日志和测试临时目录不是源码；源码包不包含这些目录，也不包含 `.env` 密钥。', '']
    (ROOT / 'SOURCE_INDEX.md').write_text('\n'.join(lines), encoding='utf-8')
    if args.archive:
        archive = ROOT / 'exports' / 'knowbase-source-latest.zip'
        archive.parent.mkdir(exist_ok=True)
        with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
            for file in files + reports:
                output.write(ROOT / file, arcname=file.as_posix())
        with ZipFile(archive) as output:
            assert output.testzip() is None
            assert set(output.namelist()) == {file.as_posix() for file in files + reports}
            for file in files + reports:
                assert output.read(file.as_posix()) == (ROOT / file).read_bytes()
        print(f'Verified {len(files)} source files + {len(reports)} reports in {archive.name}')
    else:
        print(f'Indexed {len(files)} source files + {len(reports)} reports')


if __name__ == '__main__':
    main()
