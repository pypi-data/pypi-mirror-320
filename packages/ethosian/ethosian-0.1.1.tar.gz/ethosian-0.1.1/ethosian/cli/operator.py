from pathlib import Path
from typing import Optional, List

from typer import launch as typer_launch

from ethosian.cli.settings import ethosian_cli_settings, ethosian_cli_DIR
from ethosian.cli.config import ethosianCliConfig
from ethosian.cli.console import print_info, print_heading
from ethosian.infra.type import InfraType
from ethosian.infra.resources import InfraResources
from ethosian.utils.log import logger


def delete_ethosian_conf() -> None:
    from ethosian.utils.filesystem import delete_from_fs

    logger.debug("Removing existing ethosian configuration")
    delete_from_fs(ethosian_cli_DIR)


def authenticate_user() -> None:
    """Authenticate the user using credentials from ethosian.com
    Steps:
    1. Authenticate the user by opening the ethosian sign-in url
        and the web-app will post an auth token to a mini http server
        running on the auth_server_port.
    2. Using the auth_token, authenticate the CLI with the api and get the user.
    3. After the user is authenticated update the ethosianCliConfig.
    4. Save the auth_token locally for future use.
    """
    from ethosian.api.user import authenticate_and_get_user
    from ethosian.api.schemas.user import UserSchema
    from ethosian.cli.credentials import save_auth_token
    from ethosian.cli.auth_server import (
        get_port_for_auth_server,
        get_auth_token_from_web_flow,
    )

    print_heading("Authenticating with ethosian.com ...")

    auth_server_port = get_port_for_auth_server()
    redirect_uri = "http%3A%2F%2Flocalhost%3A{}%2F".format(auth_server_port)
    auth_url = "{}?source=cli&action=signin&redirecturi={}".format(
        ethosian_cli_settings.signin_url, redirect_uri)
    print_info("\nYour browser will be opened to visit:\n{}".format(auth_url))
    typer_launch(auth_url)
    print_info("\nWaiting for a response from browser...\n")

    auth_token = get_auth_token_from_web_flow(auth_server_port)
    if auth_token is None:
        logger.error(
            "Could not authenticate, please set ethosian_API_KEY or try again")
        return

    ethosian_config: Optional[ethosianCliConfig] = ethosianCliConfig.from_saved_config(
    )
    existing_user: Optional[UserSchema] = ethosian_config.user if ethosian_config is not None else None
    # Authenticate the user and claim any workspaces from anon user
    try:
        user: Optional[UserSchema] = authenticate_and_get_user(
            auth_token=auth_token, existing_user=existing_user)
    except Exception as e:
        logger.exception(e)
        logger.error(
            "Could not authenticate, please set ethosian_API_KEY or try again")
        return

    # Save the auth token if user is authenticated
    if user is not None:
        save_auth_token(auth_token)
    else:
        logger.error(
            "Could not authenticate, please set ethosian_API_KEY or try again")
        return

    if ethosian_config is None:
        ethosian_config = ethosianCliConfig(user)
        ethosian_config.save_config()
    else:
        ethosian_config.user = user

    print_info("Welcome {}".format(user.email))


def initialize_ethosian(reset: bool = False, login: bool = False) -> Optional[ethosianCliConfig]:
    """Initialize ethosian on the users machine.

    Steps:
    1. Check if ethosian_cli_DIR exists, if not, create it. If reset == True, recreate ethosian_cli_DIR.
    2. Authenticates the user if login == True.
    3. If ethosianCliConfig exists and auth is valid, returns ethosianCliConfig.
    """
    from ethosian.utils.filesystem import delete_from_fs
    from ethosian.api.user import create_anon_user

    print_heading("Welcome to ethosian!")
    if reset:
        delete_ethosian_conf()

    logger.debug("Initializing ethosian")

    # Check if ~/.ethosian exists, if it is not a dir - delete it and create the dir
    if ethosian_cli_DIR.exists():
        logger.debug(f"{ethosian_cli_DIR} exists")
        if not ethosian_cli_DIR.is_dir():
            try:
                delete_from_fs(ethosian_cli_DIR)
            except Exception as e:
                logger.exception(e)
                raise Exception(f"Something went wrong, please delete {
                                ethosian_cli_DIR} and run again")
            ethosian_cli_DIR.mkdir(parents=True, exist_ok=True)
    else:
        ethosian_cli_DIR.mkdir(parents=True)
        logger.debug(f"Created {ethosian_cli_DIR}")

    # Confirm ethosian_cli_DIR exists otherwise we should return
    if ethosian_cli_DIR.exists():
        logger.debug(f"ethosian config location: {ethosian_cli_DIR}")
    else:
        raise Exception("Something went wrong, please try again")

    ethosian_config: Optional[ethosianCliConfig] = ethosianCliConfig.from_saved_config(
    )
    if ethosian_config is None:
        logger.debug("Creating new ethosianCliConfig")
        ethosian_config = ethosianCliConfig()
        ethosian_config.save_config()

    # Authenticate user
    if login:
        authenticate_user()
    else:
        anon_user = create_anon_user()
        if anon_user is not None and ethosian_config is not None:
            ethosian_config.user = anon_user

    logger.debug("ethosian initialized")
    return ethosian_config


def sign_in_using_cli() -> None:
    from getpass import getpass
    from ethosian.api.user import sign_in_user
    from ethosian.api.schemas.user import UserSchema, EmailPasswordAuthSchema

    print_heading("Log in")
    email_raw = input("email: ")
    pass_raw = getpass()

    if email_raw is None or pass_raw is None:
        logger.error("Incorrect email or password")

    try:
        user: Optional[UserSchema] = sign_in_user(
            EmailPasswordAuthSchema(email=email_raw, password=pass_raw))
    except Exception as e:
        logger.exception(e)
        logger.error("Could not authenticate, please try again")
        return

    if user is None:
        logger.error("Could not get user, please try again")
        return

    ethosian_config: Optional[ethosianCliConfig] = ethosianCliConfig.from_saved_config(
    )
    if ethosian_config is None:
        ethosian_config = ethosianCliConfig(user)
        ethosian_config.save_config()
    else:
        ethosian_config.user = user

    print_info("Welcome {}".format(user.email))


def start_resources(
    ethosian_config: ethosianCliConfig,
    resources_file_path: Path,
    target_env: Optional[str] = None,
    target_infra: Optional[InfraType] = None,
    target_group: Optional[str] = None,
    target_name: Optional[str] = None,
    target_type: Optional[str] = None,
    dry_run: Optional[bool] = False,
    auto_confirm: Optional[bool] = False,
    force: Optional[bool] = None,
    pull: Optional[bool] = False,
) -> None:
    print_heading(f"Starting resources in: {resources_file_path}")
    logger.debug(f"\ttarget_env   : {target_env}")
    logger.debug(f"\ttarget_infra : {target_infra}")
    logger.debug(f"\ttarget_name  : {target_name}")
    logger.debug(f"\ttarget_type  : {target_type}")
    logger.debug(f"\ttarget_group : {target_group}")
    logger.debug(f"\tdry_run      : {dry_run}")
    logger.debug(f"\tauto_confirm : {auto_confirm}")
    logger.debug(f"\tforce        : {force}")
    logger.debug(f"\tpull         : {pull}")

    from ethosian.workspace.config import WorkspaceConfig

    if not resources_file_path.exists():
        logger.error(f"File does not exist: {resources_file_path}")
        return

    # Get resource groups to deploy
    resource_groups_to_create: List[InfraResources] = WorkspaceConfig.get_resources_from_file(
        resource_file=resources_file_path,
        env=target_env,
        infra=target_infra,
        order="create",
    )

    # Track number of resource groups created
    num_rgs_created = 0
    num_rgs_to_create = len(resource_groups_to_create)
    # Track number of resources created
    num_resources_created = 0
    num_resources_to_create = 0

    if num_rgs_to_create == 0:
        print_info("No resources to create")
        return

    logger.debug(f"Deploying {num_rgs_to_create} resource groups")
    for rg in resource_groups_to_create:
        _num_resources_created, _num_resources_to_create = rg.create_resources(
            group_filter=target_group,
            name_filter=target_name,
            type_filter=target_type,
            dry_run=dry_run,
            auto_confirm=auto_confirm,
            force=force,
            pull=pull,
        )
        if _num_resources_created > 0:
            num_rgs_created += 1
        num_resources_created += _num_resources_created
        num_resources_to_create += _num_resources_to_create
        logger.debug(f"Deployed {num_resources_created} resources in {
                     num_rgs_created} resource groups")

    if dry_run:
        return

    if num_resources_created == 0:
        return

    print_heading(
        f"\n--**-- ResourceGroups deployed: {num_rgs_created}/{num_rgs_to_create}\n")
    if num_resources_created != num_resources_to_create:
        logger.error("Some resources failed to create, please check logs")


def stop_resources(
    ethosian_config: ethosianCliConfig,
    resources_file_path: Path,
    target_env: Optional[str] = None,
    target_infra: Optional[InfraType] = None,
    target_group: Optional[str] = None,
    target_name: Optional[str] = None,
    target_type: Optional[str] = None,
    dry_run: Optional[bool] = False,
    auto_confirm: Optional[bool] = False,
    force: Optional[bool] = None,
) -> None:
    print_heading(f"Stopping resources in: {resources_file_path}")
    logger.debug(f"\ttarget_env   : {target_env}")
    logger.debug(f"\ttarget_infra : {target_infra}")
    logger.debug(f"\ttarget_name  : {target_name}")
    logger.debug(f"\ttarget_type  : {target_type}")
    logger.debug(f"\ttarget_group : {target_group}")
    logger.debug(f"\tdry_run      : {dry_run}")
    logger.debug(f"\tauto_confirm : {auto_confirm}")
    logger.debug(f"\tforce        : {force}")

    from ethosian.workspace.config import WorkspaceConfig

    if not resources_file_path.exists():
        logger.error(f"File does not exist: {resources_file_path}")
        return

    # Get resource groups to shutdown
    resource_groups_to_shutdown: List[InfraResources] = WorkspaceConfig.get_resources_from_file(
        resource_file=resources_file_path,
        env=target_env,
        infra=target_infra,
        order="create",
    )

    # Track number of resource groups deleted
    num_rgs_shutdown = 0
    num_rgs_to_shutdown = len(resource_groups_to_shutdown)
    # Track number of resources created
    num_resources_shutdown = 0
    num_resources_to_shutdown = 0

    if num_rgs_to_shutdown == 0:
        print_info("No resources to delete")
        return

    logger.debug(f"Deleting {num_rgs_to_shutdown} resource groups")
    for rg in resource_groups_to_shutdown:
        _num_resources_shutdown, _num_resources_to_shutdown = rg.delete_resources(
            group_filter=target_group,
            name_filter=target_name,
            type_filter=target_type,
            dry_run=dry_run,
            auto_confirm=auto_confirm,
            force=force,
        )
        if _num_resources_shutdown > 0:
            num_rgs_shutdown += 1
        num_resources_shutdown += _num_resources_shutdown
        num_resources_to_shutdown += _num_resources_to_shutdown
        logger.debug(f"Deleted {num_resources_shutdown} resources in {
                     num_rgs_shutdown} resource groups")

    if dry_run:
        return

    if num_resources_shutdown == 0:
        return

    print_heading(
        f"\n--**-- ResourceGroups deleted: {num_rgs_shutdown}/{num_rgs_to_shutdown}\n")
    if num_resources_shutdown != num_resources_to_shutdown:
        logger.error("Some resources failed to delete, please check logs")


def patch_resources(
    ethosian_config: ethosianCliConfig,
    resources_file_path: Path,
    target_env: Optional[str] = None,
    target_infra: Optional[InfraType] = None,
    target_group: Optional[str] = None,
    target_name: Optional[str] = None,
    target_type: Optional[str] = None,
    dry_run: Optional[bool] = False,
    auto_confirm: Optional[bool] = False,
    force: Optional[bool] = None,
) -> None:
    print_heading(f"Updating resources in: {resources_file_path}")
    logger.debug(f"\ttarget_env   : {target_env}")
    logger.debug(f"\ttarget_infra : {target_infra}")
    logger.debug(f"\ttarget_name  : {target_name}")
    logger.debug(f"\ttarget_type  : {target_type}")
    logger.debug(f"\ttarget_group : {target_group}")
    logger.debug(f"\tdry_run      : {dry_run}")
    logger.debug(f"\tauto_confirm : {auto_confirm}")
    logger.debug(f"\tforce        : {force}")

    from ethosian.workspace.config import WorkspaceConfig

    if not resources_file_path.exists():
        logger.error(f"File does not exist: {resources_file_path}")
        return

    # Get resource groups to update
    resource_groups_to_patch: List[InfraResources] = WorkspaceConfig.get_resources_from_file(
        resource_file=resources_file_path,
        env=target_env,
        infra=target_infra,
        order="create",
    )

    num_rgs_patched = 0
    num_rgs_to_patch = len(resource_groups_to_patch)
    # Track number of resources updated
    num_resources_patched = 0
    num_resources_to_patch = 0

    if num_rgs_to_patch == 0:
        print_info("No resources to patch")
        return

    logger.debug(f"Patching {num_rgs_to_patch} resource groups")
    for rg in resource_groups_to_patch:
        _num_resources_patched, _num_resources_to_patch = rg.update_resources(
            group_filter=target_group,
            name_filter=target_name,
            type_filter=target_type,
            dry_run=dry_run,
            auto_confirm=auto_confirm,
            force=force,
        )
        if _num_resources_patched > 0:
            num_rgs_patched += 1
        num_resources_patched += _num_resources_patched
        num_resources_to_patch += _num_resources_to_patch
        logger.debug(f"Patched {num_resources_patched} resources in {
                     num_rgs_patched} resource groups")

    if dry_run:
        return

    if num_resources_patched == 0:
        return

    print_heading(
        f"\n--**-- ResourceGroups patched: {num_rgs_patched}/{num_rgs_to_patch}\n")
    if num_resources_patched != num_resources_to_patch:
        logger.error("Some resources failed to patch, please check logs")
