import argparse
import sys

import requests
import toml


def main():
    parser = argparse.ArgumentParser(
        description="Verify version in pyproject.toml is not already used"
    )
    parser.add_argument(
        "repo_url",
        help="Full URL to github repo that tag should be checked",
        type=str,
    )
    parser.add_argument(
        "--pyproject_file",
        help="Path to pyproject.toml file",
        default="pyproject.toml",
        type=str,
    )
    args = parser.parse_args()
    print(f"checking repo: {args.repo_url}")

    with open(args.pyproject_file, "r") as f:
        pyproject_toml = toml.load(f)
        try:
            version = pyproject_toml["project"]["version"]
        except KeyError:
            print("[project][version] not found")

            try:
                version = pyproject_toml["tool"]["poetry"]["version"]
            except KeyError:
                print("[tool][poetry][version] not found")
                sys.exit(f"version key not found in {args.pyproject_file}")

    print(f"version from file {args.pyproject_file}: {version}")

    url = f"{args.repo_url}/releases/tag/{version}"
    print(f"sending request: {url}")
    r = requests.get(url=url, stream=True)
    # 404 means such a tag is not used, 200 otherwise
    print(f"github response code: {r.status_code}")
    if r.status_code == 200:
        sys.exit(f"tag {version} from {args.pyproject_file} already exists at {url}")
    print("ok")


if __name__ == "__main__":
    main()
