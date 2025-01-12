import json
import time
from contextlib import contextmanager

import click
from aiostream import stream
from onepassword import (
    AutofillBehavior,
    ItemCategory,
    ItemCreateParams,
    ItemField,
    ItemFieldType,
    ItemSection,
    Website,
)
from onepassword.client import Client
from pyrate_limiter import Duration, InMemoryBucket, Limiter, Rate
from wakepy.modes import keep

from enpass2onepassword import __version__


async def migrate(
    ep_file,
    op_sa_name,
    op_sa_token,
    op_vault,
    ignore_non_empty,
    no_confirm,
    silent,
    skip,
    no_wakelock,
    op_rate_limit_h,
    op_rate_limit_d,
    op_client_validity_s,
):
    client, _ = await get_op_client(op_sa_name, op_sa_token)
    vaults = await client.vaults.list_all()

    if not vaults:
        click.echo(
            message=f"The 1Password Service Account '{op_sa_name}' does not have access to any vaults.",
            err=True,
        )
        raise click.Abort()

    vault = None
    async for vault in vaults:
        if vault.title == op_vault:
            vault = vault
            break

    if not vault:
        click.echo(
            message=f"The vault '{op_vault}' does not exist or "
            + f"the 1Password Service Account '{op_sa_name}' does not have access.",
            err=True,
        )
        raise click.Abort()
    op_vault_id = vault.id

    # item = await client.items.get(vault_id=op_vault_id, item_id='uuid')
    # breakpoint()

    op_items_async_iter = await client.items.list_all(vault.id)
    op_items = await stream.list(op_items_async_iter)
    if op_items and not ignore_non_empty:
        click.echo(message=f"The vault '{op_vault}' already contains items.", err=True)
        raise click.Abort()

    ep_folders, ep_items = await load_enpass_json(ep_file)

    ep_len = len(ep_items)
    if skip >= ep_len:
        if not silent:
            click.secho(f"Skipping all {ep_len} Enpass entries.", fg="yellow")
        return
    elif skip > 0:
        click.echo(
            f"Skipping {click.style(skip, fg='green')} entries of {ep_len} in total."
        )
        ep_items = ep_items[skip:]

    op_items = await map_items(ep_folders, ep_items, op_vault_id)

    if len(op_items) == 0:
        click.secho("No entries to create.", fg="yellow", bold=True)
        return

    with keep_running(not no_wakelock):
        await upload_to_onepassword(
            no_confirm,
            op_sa_name,
            op_sa_token,
            op_rate_limit_d,
            op_rate_limit_h,
            op_client_validity_s,
            silent,
            skip,
            ep_items,
            op_items,
        )


async def load_enpass_json(ep_file):
    enpass = json.load(ep_file)
    if not enpass:
        click.echo(message="Unable to load the given Enpass export.", err=True)
        raise click.Abort()

    return enpass["folders"], enpass["items"]


@contextmanager
def keep_running(enabled):
    if not enabled:
        yield

    with keep.running():
        yield


async def map_items(ep_folders, ep_items, op_vault_id):
    folders_mapping = {}
    for folder in ep_folders:
        folders_mapping[folder["uuid"]] = folder["title"]

    op_items = []
    for ep_item in ep_items:
        if ep_item.get("trashed", 0) != 0:
            continue
        if ep_item.get("archived", 0) != 0:
            continue

        op_item = await map_item(ep_item, folders_mapping, op_vault_id)
        op_items.append(op_item)

    return op_items


async def get_op_client(op_sa_name, op_sa_token):
    try:
        client = await Client.authenticate(
            auth=op_sa_token,
            integration_name=op_sa_name,
            integration_version=f"v{__version__}",
        )
    except Exception as e:
        click.echo(
            f"An error occurred while setting up the connection to 1Password: {click.style(e, fg='red')}",
            err=True,
        )
        click.echo("Check the 1Password Service Account name and token, and try again.")
        raise click.Abort()

    return client, time.time()


async def upload_to_onepassword(
    no_confirm,
    op_sa_name,
    op_sa_token,
    op_rate_limit_d,
    op_rate_limit_h,
    op_client_validity_s,
    silent,
    skip,
    ep_items,
    op_items,
):
    hourly_rate = Rate(op_rate_limit_h, Duration.HOUR)
    daily_rate = Rate(op_rate_limit_d, Duration.DAY)
    bucket = InMemoryBucket([hourly_rate, daily_rate])
    limiter = Limiter(bucket, max_delay=3_900_000)  # 1h 5min

    ep_total = len(ep_items)
    op_total = len(op_items)

    if not silent:
        entries = " remaining" if skip > 0 else ""
        click.echo(
            f"{click.style(ep_total, fg='green')}{entries} Enpass entries have been analyzed."
        )
        login_total = len(
            [item for item in op_items if item.category == ItemCategory.LOGIN]
        )
        pw_total = len(
            [item for item in op_items if item.category == ItemCategory.PASSWORD]
        )
        click.echo(
            f"{click.style(op_total, fg='green')}{entries} 1Password entries will be created."
        )
        click.echo(
            f"""
Of these, {click.style(login_total, fg='cyan')} entries are created as Logins
and {click.style(pw_total, fg='cyan')} entries are created as Passwords.
For the remaining {click.style(op_total - login_total - pw_total, fg='cyan')} entries, the category is inferred.
"""
        )

    if not no_confirm:
        click.echo("Type 'y' to continue: ", nl=False)
        c = click.getchar()
        click.echo()
        if c != "y":
            raise click.Abort()

    (client, client_created) = await get_op_client(op_sa_name, op_sa_token)
    for i, op_item in enumerate(op_items):
        try:
            # noinspection PyAsyncCall
            limiter.try_acquire("onepassword-write")

            client_age_seconds = time.time() - client_created
            if client_age_seconds > op_client_validity_s:
                (client, client_created) = await get_op_client(op_sa_name, op_sa_token)

            if not silent and i % 10 == 0:
                if i > 0:
                    click.echo()
                click.echo(f"Creating entry {skip + i} ({i} of {op_total}) ", nl=False)

            await client.items.create(op_item)
            click.echo(".", nl=False)
        except Exception as e:
            click.echo(f"Error creating entry {skip + i}: {e}", err=True)
            raise click.Abort()

    if not silent:
        click.echo()
        skipped = f" Skipped {skip} entries." if skip > 0 else ""
        click.echo(
            f"{click.style('Done.', fg='green')} Migrated {op_total} entries.{skipped}"
        )


def map_sections(item):
    default_sections = [ItemSection(id="", title="")]
    fields = item.get("fields", None)
    if not fields:
        return default_sections

    return default_sections + [
        ItemSection(id=str(field["uid"]), title=field["label"])
        for field in fields
        if field["type"] == "section"
    ]


async def map_item(ep_item, folders_mapping, op_vault_id):
    category = map_category(ep_item)
    autofill_behavior = (
        AutofillBehavior.ANYWHEREONWEBSITE
        if ep_item["auto_submit"] != 0
        else AutofillBehavior.NEVER
    )

    if category == ItemCategory.PASSWORD or category == ItemCategory.LOGIN:
        websites = [
            Website(
                url=field["value"],
                label=field["label"],
                autofill_behavior=autofill_behavior,
            )
            for field in ep_item["fields"]
            if field["type"] == "url"
        ] + [
            Website(
                url=field["value"],
                label=field["label"],
                autofill_behavior=AutofillBehavior.ANYWHEREONWEBSITE,
            )
            for field in ep_item["fields"]
            if field["type"] == ".Android#"
        ]
    else:
        websites = None

    sections = map_sections(ep_item)
    fields, category = map_fields(ep_item, category)

    op_item = ItemCreateParams(
        title=ep_item["title"],
        vault_id=op_vault_id,
        tags=(
            [folders_mapping[uuid] for uuid in ep_item["folders"]]
            if "folders" in ep_item
            else None
        ),
        category=category,
        sections=sections,
        websites=websites,
        fields=fields,
        notes=ep_item.get("note", None),
    )

    return op_item


def map_fields(item, category):
    fields = item.get("fields", None)
    if not fields:
        return [], category

    has_username = any(
        field["type"] == "username" and field["value"] != "" for field in fields
    )
    has_password = any(
        field["type"] == "password" and field["value"] != "" for field in fields
    )

    main_username_field_added = False
    main_password_field_added = False

    current_section_uid = ""

    result = []
    for field in sorted(fields, key=lambda f: f["order"]):
        if field["deleted"] != 0:
            continue
        elif field["value"] == "":
            continue
        elif field["type"] == "section":
            current_section_uid = str(field["uid"])
            continue
        elif field["type"] == ".Android#":
            continue

        field_id = str(field["uid"])
        section_id = current_section_uid
        title = field["label"].lower()

        if not main_password_field_added and field["type"] == "password":
            # set this password as main password
            section_id = None
            field_id = "password"
            title = "password"
            main_password_field_added = True
        elif (
            not has_password
            and not main_password_field_added
            and field["type"] == "pin"
        ):
            # use this pin as main password
            section_id = None
            field_id = "password"
            title = "password"
            main_password_field_added = True
        elif not main_username_field_added and field["type"] == "username":
            # use pin as password
            section_id = None
            field_id = "username"
            title = "username"
            main_username_field_added = True
        elif (
            not has_username
            and not main_username_field_added
            and field["type"] == "email"
        ):
            # use email as username
            section_id = None
            field_id = "username"
            title = "username"
            main_username_field_added = True

        sensitive = field["sensitive"] != 0

        result.append(
            ItemField(
                id=field_id,
                title=title,
                field_type=(
                    ItemFieldType.CONCEALED
                    if sensitive
                    else map_field_type(item, field)
                ),
                value=field["value"],
                section_id=section_id,
            )
        )

    if main_username_field_added and category != ItemCategory.LOGIN:
        category = ItemCategory.LOGIN
    elif (
        not main_username_field_added
        and main_password_field_added
        and ItemCategory != ItemCategory.PASSWORD
    ):
        category = ItemCategory.PASSWORD

    return result, category


field_type_map = {
    ".Android#": ItemFieldType.URL,
    "ccBankname": ItemFieldType.TEXT,
    "ccCvc": ItemFieldType.CONCEALED,
    "ccExpiry": ItemFieldType.TEXT,
    "ccName": ItemFieldType.TEXT,
    "ccNumber": ItemFieldType.CREDITCARDNUMBER,
    "ccPin": ItemFieldType.CONCEALED,
    "ccTxnpassword": ItemFieldType.CONCEALED,
    "ccType": ItemFieldType.CREDITCARDTYPE,
    "ccValidfrom": ItemFieldType.TEXT,
    "date": ItemFieldType.TEXT,
    "email": ItemFieldType.EMAIL,
    "multiline": ItemFieldType.TEXT,
    "numeric": ItemFieldType.TEXT,
    "password": ItemFieldType.CONCEALED,
    "phone": ItemFieldType.PHONE,
    "pin": ItemFieldType.CONCEALED,
    "section": ItemFieldType.UNSUPPORTED,
    "text": ItemFieldType.TEXT,
    "totp": ItemFieldType.TOTP,
    "url": ItemFieldType.URL,
    "username": ItemFieldType.TEXT,
}


def map_field_type(item, field):
    c = field_type_map.get(field["type"], None)
    if c:
        return c

    click.echo(
        f"Unexpected field type '{field['type']}' on field '{field['label']}' ({field['uid']}) "
        + f"on item '{item['title']}' ({item['uuid']})",
        err=True,
    )
    raise click.Abort()


category_map = {
    "computer": ItemCategory.ROUTER,
    "creditcard": ItemCategory.CREDITCARD,
    "finance": ItemCategory.BANKACCOUNT,
    "identity": ItemCategory.IDENTITY,
    "license": ItemCategory.SOFTWARELICENSE,
    "login": ItemCategory.LOGIN,
    "misc": ItemCategory.SECURENOTE,
    "note": ItemCategory.SECURENOTE,
    "password": ItemCategory.PASSWORD,
    "travel": ItemCategory.PASSPORT,
    "uncategorized": ItemCategory.LOGIN,
}


def map_category(item):
    c = category_map.get(item["category"], None)
    if c:
        return c

    click.echo(
        f"Unexpected category '{item['category']}' on item '{item['title']}' ({item['uuid']})",
        err=True,
    )
    raise click.Abort()
