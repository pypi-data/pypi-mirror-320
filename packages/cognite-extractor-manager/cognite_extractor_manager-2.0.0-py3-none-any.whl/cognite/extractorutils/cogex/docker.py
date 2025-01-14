import os
import subprocess
from time import time
from typing import List, Tuple

from cognite.extractorutils.cogex._common import get_pyproject
from cognite.extractorutils.cogex.io import fail, headerprint, lineprint

_dockerfile_template = """
FROM {docker_base}
RUN apt-get update && apt-get upgrade -y

{preamble}
{mkdirs}

{user}

RUN set -ex && pip install --upgrade pip && pip install uv pipx
{set_path}

WORKDIR {installdir}

COPY pyproject.toml ./
COPY uv.lock ./
{copy_packages}

COPY build/config_remote.yaml /config/config_remote.yaml

RUN pipx install .

WORKDIR {workdir}

ENTRYPOINT [ "{entrypoint}" ]
CMD ["{default_arg}"]
"""

_remote_configfile = """
type: remote
cognite:
    # Read these from environment variables
    host: ${COGNITE_BASE_URL}
    project: ${COGNITE_PROJECT}

    idp-authentication:
        token-url: ${COGNITE_TOKEN_URL}

        client-id: ${COGNITE_CLIENT_ID}
        secret: ${COGNITE_CLIENT_SECRET}
        scopes:
            - ${COGNITE_BASE_URL}/.default

    extraction-pipeline:
        external-id: ${COGNITE_EXTRACTION_PIPELINE}
"""


def _get_python_version() -> Tuple[int, int, int]:
    raw_version = subprocess.check_output(["uv", "run", "python", "-V"]).decode("ascii").replace("Python", "").strip()
    print(f"Detected python version {raw_version}")
    raw_parts = raw_version.split(".")
    return int(raw_parts[0]), int(raw_parts[1]), int(raw_parts[2])


def _get_entrypoint() -> str:
    pyproject = get_pyproject()
    scripts = pyproject["project"].get("scripts", [])

    if len(scripts) == 0:
        raise ValueError("No scripts found in [project.scripts], can't deduce entrypoint")
    elif len(scripts) > 1:
        try:
            entrypoint = pyproject["tool"]["cogex"]["docker"]["entrypoint"]
        except KeyError:
            raise ValueError(
                "Multiple scripts found in [project.scripts], "
                "please specify which is the entrypoint in 'entrypoint' under [tool.cogex.docker]"
            )

        if entrypoint not in scripts:
            raise ValueError(f"Given entrypoint {entrypoint} is not listed under [project.scripts]")

        return entrypoint
    else:
        entrypoint = list(scripts.keys())[0]

    print(f"Using entrypoint '{entrypoint}' ({scripts[entrypoint].split(':')[0]})")
    return entrypoint


def _get_packages() -> List[str]:
    pyproject = get_pyproject()

    try:
        packages = pyproject["tool"]["cogex"]["docker"]["packages"]
    except KeyError:
        packages = [pyproject["project"]["name"].replace("-", "_")]
        print(f"No [tool.cogex.docker.packages] found, guessing {packages}")

    return packages


def _get_docker_base() -> str:
    try:
        base = get_pyproject()["tool"]["cogex"]["docker"]["base-image"]

    except KeyError:
        python_version = _get_python_version()
        base = f"python:{python_version[0]}.{python_version[1]}-slim"

    print(f"Using base image {base}")
    return base


def create_dockerfile() -> None:
    headerprint("Generating Dockerfile")
    pyproject = get_pyproject()
    packages = _get_packages()

    try:
        dockerconfig = pyproject["tool"]["cogex"]["docker"]
    except KeyError:
        raise ValueError("No [tool.cogex.docker] section in pyproject")

    preamble = dockerconfig.get("preamble", "")
    if preamble:
        print("Including preamble")

    copy_statements = ["COPY {} {}".format(p, p) for p in packages]

    if "readme" in pyproject["project"]:
        copy_statements.append(f"RUN touch {pyproject['project']['readme']}")
    copy_packages = "\n".join(copy_statements)

    installdir = dockerconfig.get("install-dir", pyproject["project"]["name"].replace(" ", "_"))
    workdir = dockerconfig.get("work-dir", installdir)

    dirs = ["/config", "/logs", installdir]
    if workdir not in dirs and workdir != "/":
        dirs.append(workdir)
    mkdirs = "\n".join([f"RUN mkdir -p {dir}" for dir in dirs])

    username = dockerconfig.get("user-name", "root")
    userid = dockerconfig.get("user-id", 0 if username == "root" else 1000)
    groupid = dockerconfig.get("group-id", userid)

    if userid:
        statements = []
        statements.append(f"RUN groupadd -g {groupid} {username} && useradd -m -u {userid} -g {username} {username}")

        if workdir != installdir:
            if workdir == "/":
                print("Warning: Setting workdir to / with a non-root user might cause problems")
            else:
                statements.append(f"RUN chown -R {username}:{username} {workdir}")
                statements.append(f"RUN chmod -R a+rw {workdir}")

        statements.append(f"RUN chown -R {username}:{username} {installdir}")
        statements.append(f"RUN chmod -R a+r {installdir}")
        statements.append(f"RUN chown -R {username}:{username} /config")
        statements.append("RUN chmod -R a+r /config")
        statements.append(f"RUN chown -R {username}:{username} /logs")
        statements.append("RUN chmod -R a+rw /logs")
        statements.append(f"USER {username}")

        set_user = "\n".join(statements)
        set_path = f"ENV PATH /home/{username}/.local/bin:$PATH"
    else:
        set_user = "USER root"
        set_path = "ENV PATH /root/.local/bin:$PATH"

    default_arg = dockerconfig.get("default-argument", "/config/config_remote.yaml")

    with open(f"build{os.path.sep}Dockerfile", "w") as dockerfile:
        dockerfile.write(
            _dockerfile_template.format(
                docker_base=_get_docker_base(),
                preamble=preamble,
                workdir=workdir,
                installdir=installdir,
                copy_packages=copy_packages,
                entrypoint=_get_entrypoint(),
                user=set_user,
                set_path=set_path,
                default_arg=default_arg,
                mkdirs=mkdirs,
            ).lstrip()
        )
    print(f"Dockerfile created at build{os.path.sep}Dockerfile")

    with open(f"build{os.path.sep}config_remote.yaml", "w") as remote_config:
        remote_config.write(_remote_configfile)


def build_docker_image() -> None:
    start_time = time()

    pyproject = get_pyproject()

    version: str = pyproject["project"]["version"].strip()
    major: str = version.split(".")[0]

    try:
        tags = [tag.format(version=version, major=major) for tag in pyproject["tool"]["cogex"]["docker"]["tags"]]
    except KeyError:
        raise ValueError("No docker tags listed in 'tags' under [tool.cogex.docker]")

    create_dockerfile()

    headerprint("Building Docker image")
    formatted_tags = " ".join([f"-t {tag}" for tag in tags])
    if os.system(f"docker build . -f build{os.path.sep}Dockerfile {formatted_tags}"):
        lineprint("red")
        fail("Could not build docker image")

    lineprint()
    headerprint("Build done")
    print(f"Tagged docker images: {', '.join(tags)}")
    print(f"Total build time: {time() - start_time:.1f} s")
    print()
