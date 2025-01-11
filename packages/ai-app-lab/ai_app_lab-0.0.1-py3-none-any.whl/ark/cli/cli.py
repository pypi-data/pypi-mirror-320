import os
import shutil
import time
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from ark.cli.utils import TosSDKDownloader, VeFaaS, get_default_cr_host
from ark.cli.utils.vefaas import InvalidOperationError
from ark.core.launcher.local.serve import launch_serve

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def push(
    name: Annotated[str, typer.Argument(help="Project Name")],
    *,
    user_name: Annotated[
        str,
        typer.Option(
            help="Image Repository User name",
        ),
    ],
    password: Annotated[str, typer.Option(help="Image Repository Password")],
    ak: Annotated[
        str,
        typer.Option(help="Volcengine AccessKey"),
    ],
    sk: Annotated[str, typer.Option(help="Volcengine SecretKey")],
    release: Annotated[bool, typer.Option(help="Release the function")] = False,
    sdk_version: Annotated[
        Optional[str], typer.Option(help="SDK version for image to install")
    ] = None,
    cr_host: Annotated[
        Optional[str], typer.Option(help="Image Repository Host")
    ] = get_default_cr_host(),
    cr_namespace: Annotated[
        Optional[str], typer.Option(help="Image Repository Namespace")
    ] = None,
    image_name: Annotated[Optional[str], typer.Option(help="Image Name")] = None,
    image_version: Annotated[
        Optional[str], typer.Option(help="Image Tag Version")
    ] = "latest",
    bucket_name: Annotated[
        Optional[str], typer.Option(help="Tos Bucket Name")
    ] = "ark-sdk-cn-beijing",
    sdk_prefix: Annotated[
        Optional[str], typer.Option(help="Tos Sdk Prefix")
    ] = "python_sdk",
) -> None:
    try:
        import docker
    except ImportError as e:
        raise ImportError("Please install docker package to use this command.") from e

    assert isinstance(user_name, str), "please input your user name"
    assert isinstance(password, str), "please input your password"

    # image meta
    project_path = Path.cwd() / name
    cr_namespace, image_name = cr_namespace or name, image_name or name
    tag = f"{cr_host}/{cr_namespace}/{image_name}:{image_version}"
    platform = os.getenv("ARCH") or "linux/x86_64"

    # sdk arg
    tos_client = TosSDKDownloader(
        ak=ak, sk=sk, bucket_name=bucket_name, sdk_prefix=sdk_prefix
    )
    sdk_version = sdk_version or tos_client.get_latest_sdk_wheel()
    build_args = {
        "SDK_WHEEL": sdk_version,
        "SDK_URL": tos_client.get_sdk_presign_url(sdk_version),
    }

    # docker build image
    docker_client = docker.from_env()  # type: ignore
    build_logs = docker_client.api.build(
        path=project_path.__str__(),
        dockerfile=os.path.join(project_path, "Dockerfile"),
        tag=tag,
        platform=platform,
        buildargs=build_args,
    )
    for line in build_logs:
        typer.echo(line)

    typer.echo(f"Image: {tag} build successfully")

    # docker push image
    auth_config = {"username": user_name, "password": password}
    resp = docker_client.images.push(
        repository=tag, auth_config=auth_config, stream=True, decode=True
    )
    for line in resp:
        typer.echo(line)

    typer.echo(f"Image: {tag} pushed to repository successfully")

    # push function to vefaas
    try:
        vefaas_client = VeFaaS(ak=ak, sk=sk)

        function = vefaas_client.get_function_by_name(name)
        typer.echo(f"Get Function {name}, function id: {function.Id}")

        function = vefaas_client.update_function_image(function.Id, tag)
        typer.echo(f"Push function {name} successfully, function id: {function.Id}")
    except Exception as e:
        typer.echo(f"Push function {name} to vefaas failed: {e}")
        raise e

    if not release:
        return

    # release function on vefaas
    is_synced = False
    while not is_synced:
        try:
            resp = vefaas_client.release_function(function.Name, function.Id)
            is_synced = True
            typer.echo(f"Release function {name} successfully, status: {resp.Status}")
        except InvalidOperationError as e:
            assert e.is_invalid_image_status(), e
            typer.echo(f"Release function {name} failed, err:{e.message}, retrying...")
            time.sleep(10)
        except Exception as e:
            typer.echo(f"Release function {name} failed, err:{e}, stopped.")
            raise e


@app.command()
def create(name: Annotated[str, typer.Argument(help="Project Name")]) -> None:
    project_template_dir = Path(__file__).parents[0] / "serve_template"
    destination_dir = Path.cwd() / name

    # create ./{name}/code/ directory
    os.makedirs(destination_dir, exist_ok=True)
    shutil.copytree(project_template_dir, destination_dir, dirs_exist_ok=True)

    typer.echo("Initialization completed.")


@app.command()
def serve(name: Annotated[str, typer.Argument(help="Project Name")]) -> None:
    package_path: str = (Path.cwd() / name / "code/main").__str__()
    launch_serve(package_path)


if __name__ == "__main__":
    app()
