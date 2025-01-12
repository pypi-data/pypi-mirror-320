"""
recommend use:
uv run publish.py -v freeze -u

means:
-v major: update major version
-v minor: update minor version
-v patch: update patch version
-v freeze: freeze version

-u: use uv to build
-t: upload to testpypi
"""

import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    cmd = ["uv", "add", "tomli", "--dev"]
    input(f"即将执行: {cmd}, 确认工作目录, 按回车继续...")
    subprocess.run(cmd)

try:
    import click
except ImportError:
    cmd = ["uv", "add", "click", "--dev"]
    input(f"即将执行: {cmd}, 确认工作目录, 按回车继续...")
    subprocess.run(cmd)

try:
    import twine
except ImportError:
    cmd = ["uv", "add", "twine", "--dev"]
    input(f"即将执行: {cmd}, 确认工作目录, 按回车继续...")
    subprocess.run(cmd)


def clean_constructs():
    """清理所有构建文件"""
    print("🧹 清理构建文件...")
    paths = ["dist", "build", "*.egg-info"]
    for path in paths:
        for p in Path(".").glob(path):
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()


def get_current_version():
    """获取当前版本号"""
    with open("pyproject.toml", "rb") as f:
        data = tomli.load(f)
    return data["project"]["version"]


def update_version(version_type="patch"):
    """更新版本号

    Args:
        version_type: major, minor, patch, freeze
    """
    current = get_current_version()
    major, minor, patch = map(int, current.split("."))

    if version_type == "major":
        major += 1
        minor = patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    elif version_type == "freeze":
        pass

    new_version = f"{major}.{minor}.{patch}"

    # 更新 pyproject.toml
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace(f'version = "{current}"', f'version = "{new_version}"')

    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(content)

    return new_version


def build_package(uv=True):
    """构建包"""
    print("📦 构建包...")
    if uv:
        result = subprocess.run(["uv", "build"])
    else:
        result = subprocess.run([sys.executable, "-m", "build"])
    return result.returncode == 0


def upload_package(uv=True, test=False):
    """上传包

    Args:
        uv: 是否使用 uv
        test: 是否上传到测试环境
    """
    if uv:
        cmd = ["uv", "publish"]
    else:
        cmd = [sys.executable, "-m", "twine", "upload"]
    if test:
        cmd.extend(["--repository", "testpypi"])

    cmd.append("dist/*")

    print(f"📤 上传到 {'TestPyPI' if test else 'PyPI'}...")
    result = subprocess.run(cmd)
    return result.returncode == 0


@click.command()
@click.option("-t", "--test", is_flag=True, help="上传到测试环境")
@click.option(
    "-v",
    "--version-bump",
    type=click.Choice(["major", "minor", "patch", "freeze"], case_sensitive=False),
    default="patch",
    help="版本更新类型：major(主版本), minor(次版本), patch(补丁版本), freeze(冻结版本)",
    show_default=True,
)
@click.option("-u", "--uv", is_flag=True, help="使用 uv 构建")
def main(test, version_bump, uv):
    """主函数"""

    # 清理旧的构建文件
    clean_constructs()

    # 更新版本号
    new_version = update_version(version_bump)
    print(f"📝 版本号更新至 {new_version}")

    # 构建包
    if not build_package(uv=uv):
        print("❌ 构建失败")
        return

    # 上传包 # FIXME:uv publish is beta
    if not upload_package(uv=False, test=test):
        print("❌ 上传失败")
        return

    print(f"✅ 发布成功！版本: {new_version}")
    print(
        f"📦 包地址: https://{'test.' if test else ''}pypi.org/project/river_print/{new_version}/"
    )


if __name__ == "__main__":
    main()
