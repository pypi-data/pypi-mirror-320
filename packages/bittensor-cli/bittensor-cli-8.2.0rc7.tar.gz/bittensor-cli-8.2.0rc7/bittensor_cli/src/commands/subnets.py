import asyncio
import json
import sqlite3
from typing import TYPE_CHECKING, Optional, cast
import typer

from bittensor_wallet import Wallet
from bittensor_wallet.errors import KeyFileError
from rich.prompt import Confirm, Prompt
from rich.console import Console, Group
from rich.spinner import Spinner
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Column, Table
from rich import box

from bittensor_cli.src import COLOR_PALETTE, SUBNETS
from bittensor_cli.src.bittensor.balances import Balance
from bittensor_cli.src.bittensor.chain_data import SubnetState
from bittensor_cli.src.bittensor.extrinsics.registration import (
    register_extrinsic,
    burned_register_extrinsic,
)
from bittensor_cli.src.bittensor.extrinsics.root import root_register_extrinsic
from rich.live import Live
from bittensor_cli.src.bittensor.minigraph import MiniGraph
from bittensor_cli.src.commands.wallets import set_id, get_id
from bittensor_cli.src.bittensor.utils import (
    RAO_PER_TAO,
    console,
    create_table,
    err_console,
    print_verbose,
    print_error,
    format_error_message,
    get_metadata_table,
    millify_tao,
    render_table,
    update_metadata_table,
    prompt_for_identity,
    get_subnet_name,
)

if TYPE_CHECKING:
    from bittensor_cli.src.bittensor.subtensor_interface import SubtensorInterface

TAO_WEIGHT = 0.018

# helpers and extrinsics


async def register_subnetwork_extrinsic(
    subtensor: "SubtensorInterface",
    wallet: Wallet,
    subnet_identity: dict,
    wait_for_inclusion: bool = False,
    wait_for_finalization: bool = True,
    prompt: bool = False,
) -> bool:
    """Registers a new subnetwork.

        wallet (bittensor.wallet):
            bittensor wallet object.
        wait_for_inclusion (bool):
            If set, waits for the extrinsic to enter a block before returning ``true``, or returns ``false`` if the extrinsic fails to enter the block within the timeout.
        wait_for_finalization (bool):
            If set, waits for the extrinsic to be finalized on the chain before returning ``true``, or returns ``false`` if the extrinsic fails to be finalized within the timeout.
        prompt (bool):
            If true, the call waits for confirmation from the user before proceeding.
    Returns:
        success (bool):
            Flag is ``true`` if extrinsic was finalized or included in the block.
            If we did not wait for finalization / inclusion, the response is ``true``.
    """

    async def _find_event_attributes_in_extrinsic_receipt(
        response_, event_name: str
    ) -> list:
        """
        Searches for the attributes of a specified event within an extrinsic receipt.

        :param response_: (substrateinterface.base.ExtrinsicReceipt): The receipt of the extrinsic to be searched.
        :param event_name: The name of the event to search for.

        :return: A list of attributes for the specified event. Returns [-1] if the event is not found.
        """
        for event in await response_.triggered_events:
            # Access the event details
            event_details = event["event"]
            # Check if the event_id is 'NetworkAdded'
            if event_details["event_id"] == event_name:
                # Once found, you can access the attributes of the event_name
                return event_details["attributes"]
        return [-1]

    print_verbose("Fetching balance")
    your_balance_ = await subtensor.get_balance(wallet.coldkeypub.ss58_address)
    your_balance = your_balance_[wallet.coldkeypub.ss58_address]

    print_verbose("Fetching burn_cost")
    sn_burn_cost = await burn_cost(subtensor)
    if sn_burn_cost > your_balance:
        err_console.print(
            f"Your balance of: [{COLOR_PALETTE['POOLS']['TAO']}]{your_balance}[{COLOR_PALETTE['POOLS']['TAO']}] is not enough to pay the subnet lock cost of: "
            f"[{COLOR_PALETTE['POOLS']['TAO']}]{sn_burn_cost}[{COLOR_PALETTE['POOLS']['TAO']}]"
        )
        return False

    if prompt:
        console.print(
            f"Your balance is: [{COLOR_PALETTE['POOLS']['TAO']}]{your_balance}"
        )
        if not Confirm.ask(
            f"Do you want to register a subnet for [{COLOR_PALETTE['POOLS']['TAO']}]{sn_burn_cost}?"
        ):
            return False

    has_identity = any(subnet_identity.values())
    if has_identity:
        identity_data = {
            "subnet_name": subnet_identity["subnet_name"].encode(),
            "github_repo": subnet_identity["github_repo"].encode(),
            "subnet_contact": subnet_identity["subnet_contact"].encode(),
        }
        for field, value in identity_data.items():
            max_size = 64  # bytes
            if len(value) > max_size:
                err_console.print(
                    f"[red]Error:[/red] Identity field [white]{field}[/white] must be <= {max_size} bytes.\n"
                    f"Value '{value.decode()}' is {len(value)} bytes."
                )
                return False

    try:
        wallet.unlock_coldkey()
    except KeyFileError:
        err_console.print("Error decrypting coldkey (possibly incorrect password)")
        return False

    with console.status(":satellite: Registering subnet...", spinner="earth"):
        call_params = {
            "hotkey": wallet.hotkey.ss58_address,
            "mechid": 1,
        }
        call_function = "register_network"
        if has_identity:
            call_params["identity"] = identity_data
            call_function = "register_network_with_identity"

        substrate = subtensor.substrate
        # create extrinsic call
        call = await substrate.compose_call(
            call_module="SubtensorModule",
            call_function=call_function,
            call_params=call_params,
        )
        extrinsic = await substrate.create_signed_extrinsic(
            call=call, keypair=wallet.coldkey
        )
        response = await substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=wait_for_inclusion,
            wait_for_finalization=wait_for_finalization,
        )

        # We only wait here if we expect finalization.
        if not wait_for_finalization and not wait_for_inclusion:
            return True

        await response.process_events()
        if not await response.is_success:
            err_console.print(
                f":cross_mark: [red]Failed[/red]: {format_error_message(await response.error_message, substrate)}"
            )
            await asyncio.sleep(0.5)
            return False

        # Successful registration, final check for membership
        else:
            attributes = await _find_event_attributes_in_extrinsic_receipt(
                response, "NetworkAdded"
            )
            console.print(
                f":white_heavy_check_mark: [dark_sea_green3]Registered subnetwork with netuid: {attributes[0]}"
            )
            return True


# commands


async def subnets_list(
    subtensor: "SubtensorInterface",
    reuse_last: bool,
    html_output: bool,
    no_cache: bool,
    verbose: bool,
    live: bool,
):
    """List all subnet netuids in the network."""

    async def fetch_subnet_data():
        block_number = await subtensor.substrate.get_block_number(None)
        subnets = await subtensor.get_all_subnet_dynamic_info()

        # Sort subnets by market cap, keeping the root subnet in the first position
        root_subnet = next(s for s in subnets if s.netuid == 0)
        other_subnets = sorted(
            [s for s in subnets if s.netuid != 0],
            key=lambda x: (x.alpha_in.tao + x.alpha_out.tao) * x.price.tao,
            reverse=True,
        )
        sorted_subnets = [root_subnet] + other_subnets
        return sorted_subnets, block_number

    def calculate_emission_stats(
        subnets: list, block_number: int
    ) -> tuple[Balance, str]:
        # We do not include the root subnet in the emission calculation
        total_tao_emitted = sum(
            subnet.tao_in.tao for subnet in subnets if subnet.netuid != 0
        )
        emission_percentage = (total_tao_emitted / block_number) * 100
        percentage_color = "dark_sea_green" if emission_percentage < 100 else "red"
        formatted_percentage = (
            f"[{percentage_color}]{emission_percentage:.2f}%[/{percentage_color}]"
        )
        if not verbose:
            percentage_string = f"τ {millify_tao(total_tao_emitted)}/{millify_tao(block_number)} ({formatted_percentage})"
        else:
            percentage_string = f"τ {total_tao_emitted:.1f}/{block_number} ({formatted_percentage})"
        return total_tao_emitted, percentage_string

    def define_table(
        total_emissions: float,
        total_rate: float,
        total_netuids: int,
        tao_emission_percentage: str,
    ):
        table = Table(
            title=f"\n[{COLOR_PALETTE['GENERAL']['HEADER']}]Subnets"
            f"\nNetwork: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{subtensor.network}\n\n",
            show_footer=True,
            show_edge=False,
            header_style="bold white",
            border_style="bright_black",
            style="bold",
            title_justify="center",
            show_lines=False,
            pad_edge=True,
        )

        table.add_column(
            "[bold white]Netuid",
            style="grey89",
            justify="center",
            footer=str(total_netuids),
        )
        table.add_column("[bold white]Name", style="cyan", justify="left")
        table.add_column(
            f"[bold white]Price \n({Balance.get_unit(0)}_in/{Balance.get_unit(1)}_in)",
            style="dark_sea_green2",
            justify="left",
            footer=f"τ {total_rate}",
        )
        table.add_column(
            f"[bold white]Market Cap \n({Balance.get_unit(1)} * Price)",
            style="steel_blue3",
            justify="left",
        )
        table.add_column(
            f"[bold white]Emission ({Balance.get_unit(0)})",
            style=COLOR_PALETTE["POOLS"]["EMISSION"],
            justify="left",
            footer=f"τ {total_emissions}",
        )
        table.add_column(
            f"[bold white]P ({Balance.get_unit(0)}_in, {Balance.get_unit(1)}_in)",
            style=COLOR_PALETTE["STAKE"]["TAO"],
            justify="left",
            footer=f"{tao_emission_percentage}",
        )
        table.add_column(
            f"[bold white]Stake ({Balance.get_unit(1)}_out)",
            style=COLOR_PALETTE["STAKE"]["STAKE_ALPHA"],
            justify="left",
        )
        table.add_column(
            f"[bold white]Supply ({Balance.get_unit(1)})",
            style=COLOR_PALETTE["POOLS"]["ALPHA_IN"],
            justify="left",
        )

        table.add_column(
            "[bold white]Tempo (k/n)",
            style=COLOR_PALETTE["GENERAL"]["TEMPO"],
            justify="left",
            overflow="fold",
        )
        return table

    # Non-live mode
    def create_table(subnets, block_number):
        rows = []
        _, percentage_string = calculate_emission_stats(subnets, block_number)

        for subnet in subnets:
            netuid = subnet.netuid
            symbol = f"{subnet.symbol}\u200e"

            if netuid == 0:
                emission_tao = 0.0
            else:
                emission_tao = subnet.emission.tao

            alpha_in_value = (
                f"{millify_tao(subnet.alpha_in.tao)}"
                if not verbose
                else f"{subnet.alpha_in.tao:,.4f}"
            )
            alpha_out_value = (
                f"{millify_tao(subnet.alpha_out.tao)}"
                if not verbose
                else f"{subnet.alpha_out.tao:,.4f}"
            )
            price_value = (
                f"{millify_tao(subnet.price.tao)}"
                if not verbose
                else f"{subnet.price.tao:,.4f}"
            )

            # Market Cap
            market_cap = (subnet.alpha_in.tao + subnet.alpha_out.tao) * subnet.price.tao
            market_cap_value = (
                f"{millify_tao(market_cap)}" if not verbose else f"{market_cap:,.4f}"
            )

            # Liquidity
            tao_in_cell = (
                (
                    f"τ {millify_tao(subnet.tao_in.tao)}"
                    if not verbose
                    else f"τ {subnet.tao_in.tao:,.4f}"
                )
                if netuid != 0
                else "-"
            )

            alpha_in_cell = f"{alpha_in_value} {symbol}" if netuid != 0 else "-"

            # Supply
            supply = subnet.alpha_in.tao + subnet.alpha_out.tao
            supply_value = f"{millify_tao(supply)}" if not verbose else f"{supply:,.4f}"

            # Prepare cells
            netuid_cell = str(netuid)
            subnet_name_cell = (
                f"[{COLOR_PALETTE['GENERAL']['SYMBOL']}]{subnet.symbol if netuid != 0 else 'τ'}[/{COLOR_PALETTE['GENERAL']['SYMBOL']}]"
                f" {get_subnet_name(subnet)}"
            )
            emission_cell = f"τ {emission_tao:,.4f}"
            price_cell = f"{price_value} τ/{symbol}"
            liquidity_cell = f"{tao_in_cell}, {alpha_in_cell}"
            alpha_out_cell = (
                f"{alpha_out_value} {symbol}"
                if netuid != 0
                else f"{symbol} {alpha_out_value}"
            )
            market_cap_cell = f"τ {market_cap_value}"
            supply_cell = f"{supply_value} {symbol} [#806DAF]/21M"

            if netuid != 0:
                tempo_cell = f"{subnet.blocks_since_last_step}/{subnet.tempo}"
            else:
                tempo_cell = "-/-"

            rows.append(
                (
                    netuid_cell,  # Netuid
                    subnet_name_cell,  # Name
                    price_cell,  # Rate τ_in/α_in
                    market_cap_cell,  # Market Cap
                    emission_cell,  # Emission (τ)
                    liquidity_cell,  # Liquidity (t_in, a_in)
                    alpha_out_cell,  # Stake α_out
                    supply_cell,  # Supply
                    tempo_cell,  # Tempo k/n
                )
            )

        total_emissions = round(
            sum(float(subnet.emission.tao) for subnet in subnets if subnet.netuid != 0),
            4,
        )
        total_rate = round(
            sum(float(subnet.price.tao) for subnet in subnets if subnet.netuid != 0), 4
        )
        total_netuids = len(subnets)
        table = define_table(
            total_emissions, total_rate, total_netuids, percentage_string
        )

        for row in rows:
            table.add_row(*row)
        return table

    # Live mode
    def create_table_live(subnets, previous_data, block_number):
        def format_cell(
            value, previous_value, unit="", unit_first=False, precision=4, millify=False
        ):
            if previous_value is not None:
                change = value - previous_value
                if abs(change) > 10 ** (-precision):
                    formatted_change = (
                        f"{change:.{precision}f}"
                        if not millify
                        else f"{millify_tao(change)}"
                    )
                    change_text = (
                        f" [pale_green3](+{formatted_change})[/pale_green3]"
                        if change > 0
                        else f" [hot_pink3]({formatted_change})[/hot_pink3]"
                    )
                else:
                    change_text = ""
            else:
                change_text = ""
            formatted_value = (
                f"{value:,.{precision}f}" if not millify else millify_tao(value)
            )
            return (
                f"{formatted_value} {unit}{change_text}"
                if not unit_first
                else f"{unit} {formatted_value}{change_text}"
            )

        def format_liquidity_cell(
            tao_val,
            alpha_val,
            prev_tao,
            prev_alpha,
            symbol,
            precision=4,
            millify=False,
            netuid=None,
        ):
            """Format liquidity cell with combined changes"""

            tao_str = (
                f"τ {millify_tao(tao_val)}"
                if millify
                else f"τ {tao_val:,.{precision}f}"
            )
            _alpha_str = f"{millify_tao(alpha_val) if millify else f'{alpha_val:,.{precision}f}'}"
            alpha_str = (
                f"{_alpha_str} {symbol}" if netuid != 0 else f"{symbol} {_alpha_str}"
            )

            # Show delta
            if prev_tao is not None and prev_alpha is not None:
                tao_change = tao_val - prev_tao
                alpha_change = alpha_val - prev_alpha

                # Show changes if either value changed
                if abs(tao_change) > 10 ** (-precision) or abs(alpha_change) > 10 ** (
                    -precision
                ):
                    if millify:
                        tao_change_str = (
                            f"+{millify_tao(tao_change)}"
                            if tao_change > 0
                            else f"{millify_tao(tao_change)}"
                        )
                        alpha_change_str = (
                            f"+{millify_tao(alpha_change)}"
                            if alpha_change > 0
                            else f"{millify_tao(alpha_change)}"
                        )
                    else:
                        tao_change_str = (
                            f"+{tao_change:.{precision}f}"
                            if tao_change > 0
                            else f"{tao_change:.{precision}f}"
                        )
                        alpha_change_str = (
                            f"+{alpha_change:.{precision}f}"
                            if alpha_change > 0
                            else f"{alpha_change:.{precision}f}"
                        )

                    changes_str = (
                        f" [pale_green3]({tao_change_str}[/pale_green3]"
                        if tao_change > 0
                        else f" [hot_pink3]({tao_change_str}[/hot_pink3]"
                        if tao_change < 0
                        else f" [white]({tao_change_str}[/white]"
                    )
                    changes_str += (
                        f"[pale_green3],{alpha_change_str})[/pale_green3]"
                        if alpha_change > 0
                        else f"[hot_pink3],{alpha_change_str})[/hot_pink3]"
                        if alpha_change < 0
                        else f"[white],{alpha_change_str})[/white]"
                    )
                    return f"{tao_str}, {alpha_str}{changes_str}"

            return f"{tao_str}, {alpha_str}"

        rows = []
        current_data = {}  # To store current values for comparison in the next update
        _, percentage_string = calculate_emission_stats(subnets, block_number)

        for subnet in subnets:
            netuid = subnet.netuid
            symbol = f"{subnet.symbol}\u200e"

            if netuid == 0:
                emission_tao = 0.0
            else:
                emission_tao = subnet.emission.tao

            market_cap = (subnet.alpha_in.tao + subnet.alpha_out.tao) * subnet.price.tao
            supply = subnet.alpha_in.tao + subnet.alpha_out.tao

            # Store current values for comparison
            current_data[netuid] = {
                "market_cap": market_cap,
                "emission_tao": emission_tao,
                "alpha_out": subnet.alpha_out.tao,
                "tao_in": subnet.tao_in.tao,
                "alpha_in": subnet.alpha_in.tao,
                "price": subnet.price.tao,
                "supply": supply,
                "blocks_since_last_step": subnet.blocks_since_last_step,
            }
            prev = previous_data.get(netuid) if previous_data else {}

            # Prepare cells
            if netuid == 0:
                unit_first = True
            else:
                unit_first = False

            netuid_cell = str(netuid)
            subnet_name_cell = (
                f"[{COLOR_PALETTE['GENERAL']['SYMBOL']}]{subnet.symbol if netuid != 0 else 'τ'}[/{COLOR_PALETTE['GENERAL']['SYMBOL']}]"
                f" {get_subnet_name(subnet)}"
            )
            emission_cell = format_cell(
                emission_tao,
                prev.get("emission_tao"),
                unit="τ",
                unit_first=True,
                precision=4,
            )
            price_cell = format_cell(
                subnet.price.tao,
                prev.get("price"),
                unit=f"τ/{symbol}",
                precision=4,
                millify=True if not verbose else False,
            )

            alpha_out_cell = format_cell(
                subnet.alpha_out.tao,
                prev.get("alpha_out"),
                unit=f"{symbol}",
                unit_first=unit_first,
                precision=5,
                millify=True if not verbose else False,
            )
            liquidity_cell = (
                format_liquidity_cell(
                    subnet.tao_in.tao,
                    subnet.alpha_in.tao,
                    prev.get("tao_in"),
                    prev.get("alpha_in"),
                    symbol,
                    precision=4,
                    millify=not verbose,
                    netuid=netuid,
                )
                if netuid != 0
                else "-, -"
            )

            market_cap_cell = format_cell(
                market_cap,
                prev.get("market_cap"),
                unit="τ",
                unit_first=True,
                precision=4,
                millify=True if not verbose else False,
            )

            # Supply cell
            supply_cell = format_cell(
                supply,
                prev.get("supply"),
                unit=f"{symbol} [#806DAF]/21M",
                unit_first=False,
                precision=2,
                millify=True if not verbose else False,
            )

            # Tempo cell
            prev_blocks_since_last_step = prev.get("blocks_since_last_step")
            if prev_blocks_since_last_step is not None:
                if subnet.blocks_since_last_step >= prev_blocks_since_last_step:
                    block_change = (
                        subnet.blocks_since_last_step - prev_blocks_since_last_step
                    )
                else:
                    # Tempo restarted
                    block_change = (
                        subnet.blocks_since_last_step + subnet.tempo + 1
                    ) - prev_blocks_since_last_step
                if block_change > 0:
                    block_change_text = f" [pale_green3](+{block_change})[/pale_green3]"
                elif block_change < 0:
                    block_change_text = f" [hot_pink3]({block_change})[/hot_pink3]"
                else:
                    block_change_text = ""
            else:
                block_change_text = ""
            tempo_cell = (
                (f"{subnet.blocks_since_last_step}/{subnet.tempo}{block_change_text}")
                if netuid != 0
                else "-/-"
            )

            rows.append(
                (
                    netuid_cell,  # Netuid
                    subnet_name_cell,  # Name
                    price_cell,  # Rate τ_in/α_in
                    market_cap_cell,  # Market Cap
                    emission_cell,  # Emission (τ)
                    liquidity_cell,  # Liquidity (t_in, a_in)
                    alpha_out_cell,  # Stake α_out
                    supply_cell,  # Supply
                    tempo_cell,  # Tempo k/n
                )
            )

        # Calculate totals
        total_netuids = len(subnets)
        _total_emissions = sum(
            float(subnet.emission.tao) for subnet in subnets if subnet.netuid != 0
        )
        total_emissions = (
            f"{millify_tao(_total_emissions)}"
            if not verbose
            else f"{_total_emissions:,.2f}"
        )

        total_rate = sum(
            float(subnet.price.tao) for subnet in subnets if subnet.netuid != 0
        )
        total_rate = (
            f"{millify_tao(total_rate)}" if not verbose else f"{total_rate:,.2f}"
        )
        table = define_table(
            total_emissions, total_rate, total_netuids, percentage_string
        )

        for row in rows:
            table.add_row(*row)
        return table, current_data

    # Live mode
    if live:
        refresh_interval = 10  # seconds

        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=20, style="green", complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            auto_refresh=True,
        )
        progress_task = progress.add_task("Updating:", total=refresh_interval)

        previous_block = None
        current_block = None
        previous_data = None

        with Live(console=console, screen=True, auto_refresh=True) as live:
            try:
                while True:
                    subnets, block_number = await fetch_subnet_data()

                    # Update block numbers
                    previous_block = current_block
                    current_block = block_number
                    new_blocks = (
                        "N/A"
                        if previous_block is None
                        else str(current_block - previous_block)
                    )

                    table, current_data = create_table_live(
                        subnets, previous_data, block_number
                    )
                    previous_data = current_data
                    progress.reset(progress_task)
                    start_time = asyncio.get_event_loop().time()

                    block_info = (
                        f"Previous: [dark_sea_green]{previous_block if previous_block else 'N/A'}[/dark_sea_green] "
                        f"Current: [dark_sea_green]{current_block}[/dark_sea_green] "
                        f"Diff: [dark_sea_green]{new_blocks}[/dark_sea_green] "
                    )

                    message = f"Live view active. Press [bold red]Ctrl + C[/bold red] to exit\n{block_info}"

                    live_render = Group(message, progress, table)
                    live.update(live_render)

                    while not progress.finished:
                        await asyncio.sleep(0.1)
                        elapsed = asyncio.get_event_loop().time() - start_time
                        progress.update(progress_task, completed=elapsed)

            except KeyboardInterrupt:
                pass  # Ctrl + C
    else:
        # Non-live mode
        subnets, block_number = await fetch_subnet_data()
        table = create_table(subnets, block_number)
        console.print(table)

        return
        # TODO: Temporarily returning till we update docs
        display_table = Prompt.ask(
            "\nPress Enter to view column descriptions or type 'q' to skip:",
            choices=["", "q"],
            default="",
        ).lower()

        if display_table == "q":
            console.print(
                f"[{COLOR_PALETTE['GENERAL']['SUBHEADING_EXTRA_1']}]Column descriptions skipped."
            )
        else:
            header = """
    [bold white]Description[/bold white]: The table displays information about each subnet. The columns are as follows:
    """
            console.print(header)
            description_table = Table(
                show_header=False, box=box.SIMPLE, show_edge=False, show_lines=True
            )

            fields = [
                ("[bold tan]Netuid[/bold tan]", "The netuid of the subnet."),
                (
                    "[bold tan]Symbol[/bold tan]",
                    "The symbol for the subnet's dynamic TAO token.",
                ),
                (
                    "[bold tan]Emission (τ)[/bold tan]",
                    "Shows how the one τ per block emission is distributed among all the subnet pools. For each subnet, this fraction is first calculated by dividing the subnet's alpha token price by the sum of all alpha prices across all the subnets. This fraction of TAO is then added to the TAO Pool (τ_in) of the subnet. This can change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#emissions[/blue].",
                ),
                (
                    "[bold tan]TAO Pool (τ_in)[/bold tan]",
                    'Number of TAO in the TAO reserves of the pool for this subnet. Attached to every subnet is a subnet pool, containing a TAO reserve and the alpha reserve. See also "Alpha Pool (α_in)" description. This can change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#subnet-pool[/blue].',
                ),
                (
                    "[bold tan]Alpha Pool (α_in)[/bold tan]",
                    "Number of subnet alpha tokens in the alpha reserves of the pool for this subnet. This reserve, together with 'TAO Pool (τ_in)', form the subnet pool for every subnet. This can change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#subnet-pool[/blue].",
                ),
                (
                    "[bold tan]STAKE (α_out)[/bold tan]",
                    "Total stake in the subnet, expressed in the subnet's alpha token currency. This is the sum of all the stakes present in all the hotkeys in this subnet. This can change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#stake-%CE%B1_out-or-alpha-out-%CE%B1_out[/blue].",
                ),
                (
                    "[bold tan]RATE (τ_in/α_in)[/bold tan]",
                    "Exchange rate between TAO and subnet dTAO token. Calculated as the reserve ratio: (TAO Pool (τ_in) / Alpha Pool (α_in)). Note that the terms relative price, alpha token price, alpha price are the same as exchange rate. This rate can change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#rate-%CF%84_in%CE%B1_in[/blue].",
                ),
                (
                    "[bold tan]Tempo (k/n)[/bold tan]",
                    'The tempo status of the subnet. Represented as (k/n) where "k" is the number of blocks elapsed since the last tempo and "n" is the total number of blocks in the tempo. The number "n" is a subnet hyperparameter and does not change every block. \nFor more, see [blue]https://docs.bittensor.com/dynamic-tao/dtao-guide#tempo-kn[/blue].',
                ),
            ]

            description_table.add_column("Field", no_wrap=True, style="bold tan")
            description_table.add_column("Description", overflow="fold")
            for field_name, description in fields:
                description_table.add_row(field_name, description)
            console.print(description_table)


async def show(
    subtensor: "SubtensorInterface",
    netuid: int,
    max_rows: Optional[int] = None,
    delegate_selection: bool = False,
    verbose: bool = False,
    prompt: bool = True,
) -> Optional[str]:
    async def show_root():
        all_subnets = await subtensor.get_all_subnet_dynamic_info()
        root_info = all_subnets[0]

        hex_bytes_result, identities, old_identities = await asyncio.gather(
            subtensor.query_runtime_api(
                runtime_api="SubnetInfoRuntimeApi",
                method="get_subnet_state",
                params=[0],
            ),
            subtensor.query_all_identities(),
            subtensor.get_delegate_identities(),
        )

        if (bytes_result := hex_bytes_result) is None:
            err_console.print("The root subnet does not exist")
            return

        if bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(bytes_result[2:])

        root_state: "SubnetState" = SubnetState.from_vec_u8(bytes_result)
        if len(root_state.hotkeys) == 0:
            err_console.print(
                "The root-subnet is currently empty with 0 UIDs registered."
            )
            return

        tao_sum = sum(
            [root_state.tao_stake[idx].tao for idx in range(len(root_state.tao_stake))]
        )

        table = Table(
            title=f"[{COLOR_PALETTE['GENERAL']['HEADER']}]Root Network\n[{COLOR_PALETTE['GENERAL']['SUBHEADING']}]Network: {subtensor.network}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]\n",
            show_footer=True,
            show_edge=False,
            header_style="bold white",
            border_style="bright_black",
            style="bold",
            title_justify="center",
            show_lines=False,
            pad_edge=True,
        )

        table.add_column("[bold white]Position", style="white", justify="center")
        # table.add_column(
        #     f"[bold white]Total Stake ({Balance.get_unit(0)})",
        #     style=COLOR_PALETTE["POOLS"]["ALPHA_IN"],
        #     justify="center",
        # )
        # ------- Temporary columns for testing -------
        # table.add_column(
        #     "Alpha (τ)",
        #     style=COLOR_PALETTE["POOLS"]["EXTRA_2"],
        #     no_wrap=True,
        #     justify="right",
        # )
        table.add_column(
            "Tao (τ)",
            style=COLOR_PALETTE["POOLS"]["EXTRA_2"],
            no_wrap=True,
            justify="right",
            footer=f"{tao_sum:.4f} τ" if verbose else f"{millify_tao(tao_sum)} τ",
        )
        # ------- End Temporary columns for testing -------
        table.add_column(
            f"[bold white]Emission ({Balance.get_unit(0)}/block)",
            style=COLOR_PALETTE["POOLS"]["EMISSION"],
            justify="center",
        )
        table.add_column(
            "[bold white]Hotkey",
            style=COLOR_PALETTE["GENERAL"]["HOTKEY"],
            justify="center",
        )
        table.add_column(
            "[bold white]Coldkey",
            style=COLOR_PALETTE["GENERAL"]["COLDKEY"],
            justify="center",
        )
        table.add_column(
            "[bold white]Identity",
            style=COLOR_PALETTE["GENERAL"]["SYMBOL"],
            justify="left",
        )

        sorted_hotkeys = sorted(
            enumerate(root_state.hotkeys),
            key=lambda x: root_state.tao_stake[x[0]],
            reverse=True,
        )
        sorted_rows = []
        sorted_hks_delegation = []
        for pos, (idx, hk) in enumerate(sorted_hotkeys):
            total_emission_per_block = 0
            for netuid_ in range(len(all_subnets)):
                subnet = all_subnets[netuid_]
                emission_on_subnet = (
                    root_state.emission_history[netuid_][idx] / subnet.tempo
                )
                total_emission_per_block += subnet.alpha_to_tao(
                    Balance.from_rao(emission_on_subnet)
                )

            # Get identity for this validator
            coldkey_identity = identities.get(root_state.coldkeys[idx], {}).get(
                "name", ""
            )
            hotkey_identity = old_identities.get(root_state.hotkeys[idx])
            validator_identity = (
                coldkey_identity
                if coldkey_identity
                else (hotkey_identity.display if hotkey_identity else "")
            )

            sorted_rows.append(
                (
                    str((pos + 1)),  # Position
                    # f"τ {millify_tao(root_state.total_stake[idx].tao)}"
                    # if not verbose
                    # else f"{root_state.total_stake[idx]}",  # Total Stake
                    # f"τ {root_state.alpha_stake[idx].tao:.4f}"
                    # if verbose
                    # else f"τ {millify_tao(root_state.alpha_stake[idx])}",  # Alpha Stake
                    f"τ {root_state.tao_stake[idx].tao:.4f}"
                    if verbose
                    else f"τ {millify_tao(root_state.tao_stake[idx])}",  # Tao Stake
                    f"{total_emission_per_block}",  # Emission
                    f"{root_state.hotkeys[idx][:6]}"
                    if not verbose
                    else f"{root_state.hotkeys[idx]}",  # Hotkey
                    f"{root_state.coldkeys[idx][:6]}"
                    if not verbose
                    else f"{root_state.coldkeys[idx]}",  # Coldkey
                    validator_identity,  # Identity
                )
            )
            sorted_hks_delegation.append(root_state.hotkeys[idx])

        for pos, row in enumerate(sorted_rows, 1):
            table_row = []
            # if delegate_selection:
            #     table_row.append(str(pos))
            table_row.extend(row)
            table.add_row(*table_row)
            if delegate_selection and pos == max_rows:
                break
        # Print the table
        console.print(table)
        console.print("\n")

        if not delegate_selection:
            tao_pool = (
                f"{millify_tao(root_info.tao_in.tao)}"
                if not verbose
                else f"{root_info.tao_in.tao:,.4f}"
            )
            stake = (
                f"{millify_tao(root_info.alpha_out.tao)}"
                if not verbose
                else f"{root_info.alpha_out.tao:,.5f}"
            )
            rate = (
                f"{millify_tao(root_info.price.tao)}"
                if not verbose
                else f"{root_info.price.tao:,.4f}"
            )
            console.print(
                f"[{COLOR_PALETTE['GENERAL']['SUBHEADING']}]Root Network (Subnet 0)[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]"
                f"\n  Rate: [{COLOR_PALETTE['GENERAL']['HOTKEY']}]{rate} τ/τ[/{COLOR_PALETTE['GENERAL']['HOTKEY']}]"
                f"\n  Emission: [{COLOR_PALETTE['GENERAL']['HOTKEY']}]τ 0[/{COLOR_PALETTE['GENERAL']['HOTKEY']}]"
                f"\n  TAO Pool: [{COLOR_PALETTE['POOLS']['ALPHA_IN']}]τ {tao_pool}[/{COLOR_PALETTE['POOLS']['ALPHA_IN']}]"
                f"\n  Stake: [{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]τ {stake}[/{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]"
                f"\n  Tempo: [{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]{root_info.blocks_since_last_step}/{root_info.tempo}[/{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]"
            )
            console.print(
                """
    Description:
        The table displays the root subnet participants and their metrics.
        The columns are as follows:
            - Position: The sorted position of the hotkey by total TAO.
            - TAO: The sum of all TAO balances for this hotkey accross all subnets. 
            - Stake: The stake balance of this hotkey on root (measured in TAO).
            - Emission: The emission accrued to this hotkey across all subnets every block measured in TAO.
            - Hotkey: The hotkey ss58 address.
            - Coldkey: The coldkey ss58 address.
    """
            )
        if delegate_selection:
            while True:
                selection = Prompt.ask(
                    "\nEnter the position of the delegate you want to stake to [dim](or press Enter to cancel)[/dim]",
                    default="",
                )

                if selection == "":
                    return None

                try:
                    idx = int(selection)
                    if 1 <= idx <= max_rows:
                        selected_hotkey = sorted_hks_delegation[idx - 1]
                        row_data = sorted_rows[idx - 1]
                        identity = "" if row_data[5] == "~" else row_data[5]
                        identity_str = f" ({identity})" if identity else ""
                        console.print(
                            f"\nSelected delegate: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{selected_hotkey}{identity_str}"
                        )

                        return selected_hotkey
                    else:
                        console.print(
                            f"[red]Invalid selection. Please enter a number between 1 and {max_rows}[/red]"
                        )
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")

    async def show_subnet(netuid_: int):
        if not await subtensor.subnet_exists(netuid=netuid):
            err_console.print(f"[red]Subnet {netuid} does not exist[/red]")
            raise typer.Exit()
        (
            _subnet_info,
            hex_bytes_result,
            identities,
            old_identities,
        ) = await asyncio.gather(
            subtensor.get_all_subnet_dynamic_info(),
            subtensor.query_runtime_api(
                runtime_api="SubnetInfoRuntimeApi",
                method="get_subnet_state",
                params=[netuid_],
            ),
            subtensor.query_all_identities(),
            subtensor.get_delegate_identities(),
        )
        subnet_info = _subnet_info[netuid_]

        if (bytes_result := hex_bytes_result) is None:
            err_console.print(f"Subnet {netuid_} does not exist")
            return

        if bytes_result.startswith("0x"):
            bytes_result = bytes.fromhex(bytes_result[2:])

        subnet_state: "SubnetState" = SubnetState.from_vec_u8(bytes_result)
        if subnet_info is None:
            err_console.print(f"Subnet {netuid_} does not exist")
            return
        elif len(subnet_state.hotkeys) == 0:
            err_console.print(
                f"Subnet {netuid_} is currently empty with 0 UIDs registered."
            )
            return

        # Define table properties
        table = Table(
            title=f"[{COLOR_PALETTE['GENERAL']['HEADER']}]Subnet [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{netuid_}"
            f"{': ' + get_subnet_name(subnet_info)}"
            f"\nNetwork: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{subtensor.network}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]\n",
            show_footer=True,
            show_edge=False,
            header_style="bold white",
            border_style="bright_black",
            style="bold",
            title_justify="center",
            show_lines=False,
            pad_edge=True,
        )

        # Add index for selection if selecting delegates
        if delegate_selection:
            table.add_column("#", style="cyan", justify="right")

        # For hotkey_block_emission calculation
        emission_sum = sum(
            [
                subnet_state.emission[idx].tao
                for idx in range(len(subnet_state.emission))
            ]
        )

        # For table footers
        alpha_sum = sum(
            [
                subnet_state.alpha_stake[idx].tao
                for idx in range(len(subnet_state.alpha_stake))
            ]
        )
        stake_sum = sum(
            [
                subnet_state.total_stake[idx].tao
                for idx in range(len(subnet_state.total_stake))
            ]
        )
        tao_sum = sum(
            [
                subnet_state.tao_stake[idx].tao * TAO_WEIGHT
                for idx in range(len(subnet_state.tao_stake))
            ]
        )
        relative_emissions_sum = 0
        owner_hotkeys = await subtensor.get_owned_hotkeys(subnet_info.owner_coldkey)
        if subnet_info.owner_hotkey not in owner_hotkeys:
            owner_hotkeys.append(subnet_info.owner_hotkey)

        owner_identity = identities.get(subnet_info.owner_coldkey, {}).get("name", "")
        if not owner_identity:
            # If no coldkey identity found, try each owner hotkey
            for hotkey in owner_hotkeys:
                if hotkey_identity := old_identities.get(hotkey):
                    owner_identity = hotkey_identity.display
                    break

        sorted_indices = sorted(
            range(len(subnet_state.hotkeys)),
            key=lambda i: (
                # Sort by owner status first
                not (
                    subnet_state.coldkeys[i] == subnet_info.owner_coldkey
                    or subnet_state.hotkeys[i] in owner_hotkeys
                ),
                # Then sort by stake amount (higher stakes first)
                -subnet_state.total_stake[i].tao,
            ),
        )

        rows = []
        for idx in sorted_indices:
            hotkey_block_emission = (
                subnet_state.emission[idx].tao / emission_sum
                if emission_sum != 0
                else 0
            )
            relative_emissions_sum += hotkey_block_emission

            # Get identity for this uid
            coldkey_identity = identities.get(subnet_state.coldkeys[idx], {}).get(
                "name", ""
            )
            hotkey_identity = old_identities.get(subnet_state.hotkeys[idx])
            uid_identity = (
                coldkey_identity
                if coldkey_identity
                else (hotkey_identity.display if hotkey_identity else "~")
            )

            if (
                subnet_state.coldkeys[idx] == subnet_info.owner_coldkey
                or subnet_state.hotkeys[idx] in owner_hotkeys
            ):
                if uid_identity == "~":
                    uid_identity = (
                        f"[dark_sea_green3](*Owner controlled)[/dark_sea_green3]"
                    )
                else:
                    uid_identity = (
                        f"[dark_sea_green3]{uid_identity} (*Owner)[/dark_sea_green3]"
                    )

            # Modify tao stake with TAO_WEIGHT
            tao_stake = subnet_state.tao_stake[idx] * TAO_WEIGHT
            rows.append(
                (
                    str(idx),  # UID
                    f"{subnet_state.total_stake[idx].tao:.4f} {subnet_info.symbol}"
                    if verbose
                    else f"{millify_tao(subnet_state.total_stake[idx])} {subnet_info.symbol}",  # Stake
                    f"{subnet_state.alpha_stake[idx].tao:.4f} {subnet_info.symbol}"
                    if verbose
                    else f"{millify_tao(subnet_state.alpha_stake[idx])} {subnet_info.symbol}",  # Alpha Stake
                    f"τ {tao_stake.tao:.4f}" if verbose else f"τ {millify_tao(tao_stake)}",  # Tao Stake
                    # str(subnet_state.dividends[idx]),
                    f"{Balance.from_tao(hotkey_block_emission).set_unit(netuid_).tao:.5f}",  # Dividends
                    f"{subnet_state.incentives[idx]:.4f}",  # Incentive
                    # f"{Balance.from_tao(hotkey_block_emission).set_unit(netuid_).tao:.5f}",  # Emissions relative
                    f"{Balance.from_tao(subnet_state.emission[idx].tao).set_unit(netuid_).tao:.5f} {subnet_info.symbol}",  # Emissions
                    f"{subnet_state.hotkeys[idx][:6]}"
                    if not verbose
                    else f"{subnet_state.hotkeys[idx]}",  # Hotkey
                    f"{subnet_state.coldkeys[idx][:6]}"
                    if not verbose
                    else f"{subnet_state.coldkeys[idx]}",  # Coldkey
                    uid_identity,  # Identity
                )
            )

        # Add columns to the table
        table.add_column("UID", style="grey89", no_wrap=True, justify="center")
        table.add_column(
            f"Stake ({Balance.get_unit(netuid_)})",
            style=COLOR_PALETTE["POOLS"]["ALPHA_IN"],
            no_wrap=True,
            justify="right",
            footer=f"{stake_sum:.4f} {subnet_info.symbol}"
            if verbose
            else f"{millify_tao(stake_sum)} {subnet_info.symbol}",
        )
        # ------- Temporary columns for testing -------
        table.add_column(
            f"Alpha ({Balance.get_unit(netuid_)})",
            style=COLOR_PALETTE["POOLS"]["EXTRA_2"],
            no_wrap=True,
            justify="right",
            footer=f"{alpha_sum:.4f} {subnet_info.symbol}"
            if verbose
            else f"{millify_tao(alpha_sum)} {subnet_info.symbol}",
        )
        table.add_column(
            "Tao (τ)",
            style=COLOR_PALETTE["POOLS"]["EXTRA_2"],
            no_wrap=True,
            justify="right",
            footer=f"{tao_sum:.4f} {subnet_info.symbol}"
            if verbose
            else f"{millify_tao(tao_sum)} {subnet_info.symbol}",
        )
        # ------- End Temporary columns for testing -------
        table.add_column(
            "Dividends",
            style=COLOR_PALETTE["POOLS"]["EMISSION"],
            no_wrap=True,
            justify="center",
            footer=f"{relative_emissions_sum:.3f}",
        )
        table.add_column("Incentive", style="#5fd7ff", no_wrap=True, justify="center")

        # Hiding relative emissions for now
        # table.add_column(
        #     "Emissions",
        #     style="light_goldenrod2",
        #     no_wrap=True,
        #     justify="center",
        #     footer=f"{relative_emissions_sum:.3f}",
        # )
        table.add_column(
            f"Emissions ({Balance.get_unit(netuid_)})",
            style=COLOR_PALETTE["POOLS"]["EMISSION"],
            no_wrap=True,
            justify="center",
            footer=str(Balance.from_tao(emission_sum).set_unit(subnet_info.netuid)),
        )
        table.add_column(
            "Hotkey",
            style=COLOR_PALETTE["GENERAL"]["HOTKEY"],
            no_wrap=True,
            justify="center",
        )
        table.add_column(
            "Coldkey",
            style=COLOR_PALETTE["GENERAL"]["COLDKEY"],
            no_wrap=True,
            justify="center",
        )
        table.add_column(
            "Identity",
            style=COLOR_PALETTE["GENERAL"]["SYMBOL"],
            no_wrap=True,
            justify="left",
        )
        for pos, row in enumerate(rows, 1):
            table_row = []
            if delegate_selection:
                table_row.append(str(pos))
            table_row.extend(row)
            table.add_row(*table_row)
            if delegate_selection and pos == max_rows:
                break

        # Print the table
        console.print("\n\n")
        console.print(table)
        console.print("\n")

        if not delegate_selection:
            subnet_name_display = f": {get_subnet_name(subnet_info)}"
            tao_pool = (
                f"{millify_tao(subnet_info.tao_in.tao)}"
                if not verbose
                else f"{subnet_info.tao_in.tao:,.4f}"
            )
            alpha_pool = (
                f"{millify_tao(subnet_info.alpha_in.tao)}"
                if not verbose
                else f"{subnet_info.alpha_in.tao:,.4f}"
            )

            console.print(
                f"[{COLOR_PALETTE['GENERAL']['SUBHEADING']}]Subnet {netuid_}{subnet_name_display}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]"
                f"\n  Owner: [{COLOR_PALETTE['GENERAL']['COLDKEY']}]{subnet_info.owner_coldkey}{' (' + owner_identity + ')' if owner_identity else ''}[/{COLOR_PALETTE['GENERAL']['COLDKEY']}]"
                f"\n  Rate: [{COLOR_PALETTE['GENERAL']['HOTKEY']}]{subnet_info.price.tao:.4f} τ/{subnet_info.symbol}[/{COLOR_PALETTE['GENERAL']['HOTKEY']}]"
                f"\n  Emission: [{COLOR_PALETTE['GENERAL']['HOTKEY']}]τ {subnet_info.emission.tao:,.4f}[/{COLOR_PALETTE['GENERAL']['HOTKEY']}]"
                f"\n  TAO Pool: [{COLOR_PALETTE['POOLS']['ALPHA_IN']}]τ {tao_pool}[/{COLOR_PALETTE['POOLS']['ALPHA_IN']}]"
                f"\n  Alpha Pool: [{COLOR_PALETTE['POOLS']['ALPHA_IN']}]{alpha_pool} {subnet_info.symbol}[/{COLOR_PALETTE['POOLS']['ALPHA_IN']}]"
                # f"\n  Stake: [{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]{subnet_info.alpha_out.tao:,.5f} {subnet_info.symbol}[/{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]"
                f"\n  Tempo: [{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]{subnet_info.blocks_since_last_step}/{subnet_info.tempo}[/{COLOR_PALETTE['STAKE']['STAKE_ALPHA']}]"
            )
    #         console.print(
    #             """
    # Description:
    #     The table displays the subnet participants and their metrics.
    #     The columns are as follows:
    #         - UID: The hotkey index in the subnet.
    #         - TAO: The sum of all TAO balances for this hotkey accross all subnets. 
    #         - Stake: The stake balance of this hotkey on this subnet.
    #         - Weight: The stake-weight of this hotkey on this subnet. Computed as an average of the normalized TAO and Stake columns of this subnet.
    #         - Dividends: Validating dividends earned by the hotkey.
    #         - Incentives: Mining incentives earned by the hotkey (always zero in the RAO demo.)
    #         - Emission: The emission accrued to this hokey on this subnet every block (in staking units).
    #         - Hotkey: The hotkey ss58 address.
    #         - Coldkey: The coldkey ss58 address.
    # """
            # )

        if delegate_selection:
            while True:
                selection = Prompt.ask(
                    "\nEnter the number of the delegate you want to stake to [dim](or press Enter to cancel)[/dim]",
                    default="",
                )

                if selection == "":
                    return None

                try:
                    idx = int(selection)
                    if 1 <= idx <= max_rows:
                        uid = int(rows[idx - 1][0])
                        hotkey = subnet_state.hotkeys[uid]
                        row_data = rows[idx - 1]
                        identity = "" if row_data[9] == "~" else row_data[9]
                        identity_str = f" ({identity})" if identity else ""
                        console.print(
                            f"\nSelected delegate: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{hotkey}{identity_str}"
                        )
                        return hotkey
                    else:
                        console.print(
                            f"[red]Invalid selection. Please enter a number between 1 and {max_rows}[/red]"
                        )
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")

        return None

    if netuid == 0:
        result = await show_root()
        return result
    else:
        result = await show_subnet(netuid)
        return result


async def burn_cost(subtensor: "SubtensorInterface") -> Optional[Balance]:
    """View locking cost of creating a new subnetwork"""
    with console.status(
        f":satellite:Retrieving lock cost from {subtensor.network}...",
        spinner="aesthetic",
    ):
        lc = await subtensor.query_runtime_api(
            runtime_api="SubnetRegistrationRuntimeApi",
            method="get_network_registration_cost",
            params=[],
        )
    if lc:
        burn_cost_ = Balance(lc)
        console.print(
            f"Subnet burn cost: [{COLOR_PALETTE['STAKE']['STAKE_AMOUNT']}]{burn_cost_}"
        )
        return burn_cost_
    else:
        err_console.print("Subnet burn cost: [red]Failed to get subnet burn cost[/red]")
        return None


async def create(
    wallet: Wallet, subtensor: "SubtensorInterface", subnet_identity: dict, prompt: bool
):
    """Register a subnetwork"""

    # Call register command.
    success = await register_subnetwork_extrinsic(
        subtensor, wallet, subnet_identity, prompt=prompt
    )
    if success and prompt:
        # Prompt for user to set identity.
        do_set_identity = Confirm.ask(
            "Would you like to set your own [blue]identity?[/blue]"
        )

        if do_set_identity:
            current_identity = await get_id(
                subtensor, wallet.coldkeypub.ss58_address, "Current on-chain identity"
            )
            if prompt:
                if not Confirm.ask(
                    "\nCost to register an [blue]Identity[/blue] is [blue]0.1 TAO[/blue],"
                    " are you sure you wish to continue?"
                ):
                    console.print(":cross_mark: Aborted!")
                    raise typer.Exit()

            identity = prompt_for_identity(
                current_identity=current_identity,
                name=None,
                web_url=None,
                image_url=None,
                discord_handle=None,
                description=None,
                additional_info=None,
            )

            await set_id(
                wallet,
                subtensor,
                identity["name"],
                identity["url"],
                identity["image"],
                identity["discord"],
                identity["description"],
                identity["additional"],
                prompt,
            )


async def pow_register(
    wallet: Wallet,
    subtensor: "SubtensorInterface",
    netuid,
    processors,
    update_interval,
    output_in_place,
    verbose,
    use_cuda,
    dev_id,
    threads_per_block,
):
    """Register neuron."""

    await register_extrinsic(
        subtensor,
        wallet=wallet,
        netuid=netuid,
        prompt=True,
        tpb=threads_per_block,
        update_interval=update_interval,
        num_processes=processors,
        cuda=use_cuda,
        dev_id=dev_id,
        output_in_place=output_in_place,
        log_verbose=verbose,
    )


async def register(
    wallet: Wallet, subtensor: "SubtensorInterface", netuid: int, prompt: bool
):
    """Register neuron by recycling some TAO."""

    # Verify subnet exists
    print_verbose("Checking subnet status")
    block_hash = await subtensor.substrate.get_chain_head()
    if not await subtensor.subnet_exists(netuid=netuid, block_hash=block_hash):
        err_console.print(f"[red]Subnet {netuid} does not exist[/red]")
        return

    # Check current recycle amount
    print_verbose("Fetching recycle amount")
    current_recycle_, balance_ = await asyncio.gather(
        subtensor.get_hyperparameter(
            param_name="Burn", netuid=netuid, block_hash=block_hash
        ),
        subtensor.get_balance(wallet.coldkeypub.ss58_address, block_hash=block_hash),
    )
    current_recycle = (
        Balance.from_rao(int(current_recycle_)) if current_recycle_ else Balance(0)
    )
    balance = balance_[wallet.coldkeypub.ss58_address]

    # Check balance is sufficient
    if balance < current_recycle:
        err_console.print(
            f"[red]Insufficient balance {balance} to register neuron. Current recycle is {current_recycle} TAO[/red]"
        )
        return

    if prompt:
        # TODO make this a reusable function, also used in subnets list
        # Show creation table.
        table = Table(
            title=f"\n[{COLOR_PALETTE['GENERAL']['HEADER']}]Register to [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]netuid: {netuid}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]"
            f"\nNetwork: [{COLOR_PALETTE['GENERAL']['SUBHEADING']}]{subtensor.network}[/{COLOR_PALETTE['GENERAL']['SUBHEADING']}]\n",
            show_footer=True,
            show_edge=False,
            header_style="bold white",
            border_style="bright_black",
            style="bold",
            title_justify="center",
            show_lines=False,
            pad_edge=True,
        )
        table.add_column(
            "Netuid", style="rgb(253,246,227)", no_wrap=True, justify="center"
        )
        table.add_column(
            "Symbol",
            style=COLOR_PALETTE["GENERAL"]["SYMBOL"],
            no_wrap=True,
            justify="center",
        )
        table.add_column(
            f"Cost ({Balance.get_unit(0)})",
            style=COLOR_PALETTE["POOLS"]["TAO"],
            no_wrap=True,
            justify="center",
        )
        table.add_column(
            "Hotkey",
            style=COLOR_PALETTE["GENERAL"]["HOTKEY"],
            no_wrap=True,
            justify="center",
        )
        table.add_column(
            "Coldkey",
            style=COLOR_PALETTE["GENERAL"]["COLDKEY"],
            no_wrap=True,
            justify="center",
        )
        table.add_row(
            str(netuid),
            f"{Balance.get_unit(netuid)}",
            f"τ {current_recycle.tao:.4f}",
            f"{wallet.hotkey.ss58_address}",
            f"{wallet.coldkeypub.ss58_address}",
        )
        console.print(table)
        if not (
            Confirm.ask(
                f"Your balance is: [{COLOR_PALETTE['GENERAL']['BALANCE']}]{balance}[/{COLOR_PALETTE['GENERAL']['BALANCE']}]\nThe cost to register by recycle is "
                f"[{COLOR_PALETTE['GENERAL']['COST']}]{current_recycle}[/{COLOR_PALETTE['GENERAL']['COST']}]\nDo you want to continue?",
                default=False,
            )
        ):
            return

    if netuid == 0:
        await root_register_extrinsic(subtensor, wallet=wallet)
    else:
        await burned_register_extrinsic(
            subtensor,
            wallet=wallet,
            netuid=netuid,
            prompt=False,
            old_balance=balance,
        )


# TODO: Confirm emissions, incentive, Dividends are to be fetched from subnet_state or keep NeuronInfo
async def metagraph_cmd(
    subtensor: Optional["SubtensorInterface"],
    netuid: Optional[int],
    reuse_last: bool,
    html_output: bool,
    no_cache: bool,
    display_cols: dict,
):
    """Prints an entire metagraph."""
    # TODO allow config to set certain columns
    if not reuse_last:
        cast("SubtensorInterface", subtensor)
        cast(int, netuid)
        with console.status(
            f":satellite: Syncing with chain: [white]{subtensor.network}[/white] ...",
            spinner="aesthetic",
        ) as status:
            block_hash = await subtensor.substrate.get_chain_head()

            if not await subtensor.subnet_exists(netuid, block_hash):
                print_error(f"Subnet with netuid: {netuid} does not exist", status)
                return False

            neurons, difficulty_, total_issuance_, block = await asyncio.gather(
                subtensor.neurons(netuid, block_hash=block_hash),
                subtensor.get_hyperparameter(
                    param_name="Difficulty", netuid=netuid, block_hash=block_hash
                ),
                subtensor.substrate.query(
                    module="SubtensorModule",
                    storage_function="TotalIssuance",
                    params=[],
                    block_hash=block_hash,
                ),
                subtensor.substrate.get_block_number(block_hash=block_hash),
            )

            hex_bytes_result = await subtensor.query_runtime_api(
                runtime_api="SubnetInfoRuntimeApi",
                method="get_subnet_state",
                params=[netuid],
            )
            if not (bytes_result := hex_bytes_result):
                err_console.print(f"Subnet {netuid} does not exist")
                return

            if bytes_result.startswith("0x"):
                bytes_result = bytes.fromhex(bytes_result[2:])

            subnet_state: "SubnetState" = SubnetState.from_vec_u8(bytes_result)

        difficulty = int(difficulty_)
        total_issuance = Balance.from_rao(total_issuance_)
        metagraph = MiniGraph(
            netuid=netuid,
            neurons=neurons,
            subtensor=subtensor,
            subnet_state=subnet_state,
            block=block,
        )
        table_data = []
        db_table = []
        total_global_stake = 0.0
        total_local_stake = 0.0
        total_rank = 0.0
        total_validator_trust = 0.0
        total_trust = 0.0
        total_consensus = 0.0
        total_incentive = 0.0
        total_dividends = 0.0
        total_emission = 0
        for uid in metagraph.uids:
            neuron = metagraph.neurons[uid]
            ep = metagraph.axons[uid]
            row = [
                str(neuron.uid),
                "{:.4f}".format(metagraph.global_stake[uid]),
                "{:.4f}".format(metagraph.local_stake[uid]),
                "{:.4f}".format(metagraph.stake_weights[uid]),
                "{:.5f}".format(metagraph.ranks[uid]),
                "{:.5f}".format(metagraph.trust[uid]),
                "{:.5f}".format(metagraph.consensus[uid]),
                "{:.5f}".format(metagraph.incentive[uid]),
                "{:.5f}".format(metagraph.dividends[uid]),
                "{}".format(int(metagraph.emission[uid] * 1000000000)),
                "{:.5f}".format(metagraph.validator_trust[uid]),
                "*" if metagraph.validator_permit[uid] else "",
                str(metagraph.block.item() - metagraph.last_update[uid].item()),
                str(metagraph.active[uid].item()),
                (
                    ep.ip + ":" + str(ep.port)
                    if ep.is_serving
                    else "[light_goldenrod2]none[/light_goldenrod2]"
                ),
                ep.hotkey[:10],
                ep.coldkey[:10],
            ]
            db_row = [
                neuron.uid,
                float(metagraph.global_stake[uid]),
                float(metagraph.local_stake[uid]),
                float(metagraph.stake_weights[uid]),
                float(metagraph.ranks[uid]),
                float(metagraph.trust[uid]),
                float(metagraph.consensus[uid]),
                float(metagraph.incentive[uid]),
                float(metagraph.dividends[uid]),
                int(metagraph.emission[uid] * 1000000000),
                float(metagraph.validator_trust[uid]),
                bool(metagraph.validator_permit[uid]),
                metagraph.block.item() - metagraph.last_update[uid].item(),
                metagraph.active[uid].item(),
                (ep.ip + ":" + str(ep.port) if ep.is_serving else "ERROR"),
                ep.hotkey[:10],
                ep.coldkey[:10],
            ]
            db_table.append(db_row)
            total_global_stake += metagraph.global_stake[uid]
            total_local_stake += metagraph.local_stake[uid]
            total_rank += metagraph.ranks[uid]
            total_validator_trust += metagraph.validator_trust[uid]
            total_trust += metagraph.trust[uid]
            total_consensus += metagraph.consensus[uid]
            total_incentive += metagraph.incentive[uid]
            total_dividends += metagraph.dividends[uid]
            total_emission += int(metagraph.emission[uid] * 1000000000)
            table_data.append(row)
        metadata_info = {
            "total_global_stake": "\u03c4 {:.5f}".format(total_global_stake),
            "total_local_stake": f"{Balance.get_unit(netuid)} "
            + "{:.5f}".format(total_local_stake),
            "rank": "{:.5f}".format(total_rank),
            "validator_trust": "{:.5f}".format(total_validator_trust),
            "trust": "{:.5f}".format(total_trust),
            "consensus": "{:.5f}".format(total_consensus),
            "incentive": "{:.5f}".format(total_incentive),
            "dividends": "{:.5f}".format(total_dividends),
            "emission": "\u03c1{}".format(int(total_emission)),
            "net": f"{subtensor.network}:{metagraph.netuid}",
            "block": str(metagraph.block.item()),
            "N": f"{sum(metagraph.active.tolist())}/{metagraph.n.item()}",
            "N0": str(sum(metagraph.active.tolist())),
            "N1": str(metagraph.n.item()),
            "issuance": str(total_issuance),
            "difficulty": str(difficulty),
            "total_neurons": str(len(metagraph.uids)),
            "table_data": json.dumps(table_data),
        }
        if not no_cache:
            update_metadata_table("metagraph", metadata_info)
            create_table(
                "metagraph",
                columns=[
                    ("UID", "INTEGER"),
                    ("GLOBAL_STAKE", "REAL"),
                    ("LOCAL_STAKE", "REAL"),
                    ("STAKE_WEIGHT", "REAL"),
                    ("RANK", "REAL"),
                    ("TRUST", "REAL"),
                    ("CONSENSUS", "REAL"),
                    ("INCENTIVE", "REAL"),
                    ("DIVIDENDS", "REAL"),
                    ("EMISSION", "INTEGER"),
                    ("VTRUST", "REAL"),
                    ("VAL", "INTEGER"),
                    ("UPDATED", "INTEGER"),
                    ("ACTIVE", "INTEGER"),
                    ("AXON", "TEXT"),
                    ("HOTKEY", "TEXT"),
                    ("COLDKEY", "TEXT"),
                ],
                rows=db_table,
            )
    else:
        try:
            metadata_info = get_metadata_table("metagraph")
            table_data = json.loads(metadata_info["table_data"])
        except sqlite3.OperationalError:
            err_console.print(
                "[red]Error[/red] Unable to retrieve table data. This is usually caused by attempting to use "
                "`--reuse-last` before running the command a first time. In rare cases, this could also be due to "
                "a corrupted database. Re-run the command (do not use `--reuse-last`) and see if that resolves your "
                "issue."
            )
            return

    if html_output:
        try:
            render_table(
                table_name="metagraph",
                table_info=f"Metagraph | "
                f"net: {metadata_info['net']}, "
                f"block: {metadata_info['block']}, "
                f"N: {metadata_info['N']}, "
                f"stake: {metadata_info['stake']}, "
                f"issuance: {metadata_info['issuance']}, "
                f"difficulty: {metadata_info['difficulty']}",
                columns=[
                    {"title": "UID", "field": "UID"},
                    {
                        "title": "Global Stake",
                        "field": "GLOBAL_STAKE",
                        "formatter": "money",
                        "formatterParams": {"symbol": "τ", "precision": 5},
                    },
                    {
                        "title": "Local Stake",
                        "field": "LOCAL_STAKE",
                        "formatter": "money",
                        "formatterParams": {
                            "symbol": f"{Balance.get_unit(netuid)}",
                            "precision": 5,
                        },
                    },
                    {
                        "title": "Stake Weight",
                        "field": "STAKE_WEIGHT",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {
                        "title": "Rank",
                        "field": "RANK",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {
                        "title": "Trust",
                        "field": "TRUST",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {
                        "title": "Consensus",
                        "field": "CONSENSUS",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {
                        "title": "Incentive",
                        "field": "INCENTIVE",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {
                        "title": "Dividends",
                        "field": "DIVIDENDS",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {"title": "Emission", "field": "EMISSION"},
                    {
                        "title": "VTrust",
                        "field": "VTRUST",
                        "formatter": "money",
                        "formatterParams": {"precision": 5},
                    },
                    {"title": "Validated", "field": "VAL"},
                    {"title": "Updated", "field": "UPDATED"},
                    {"title": "Active", "field": "ACTIVE"},
                    {"title": "Axon", "field": "AXON"},
                    {"title": "Hotkey", "field": "HOTKEY"},
                    {"title": "Coldkey", "field": "COLDKEY"},
                ],
            )
        except sqlite3.OperationalError:
            err_console.print(
                "[red]Error[/red] Unable to retrieve table data. This may indicate that your database is corrupted, "
                "or was not able to load with the most recent data."
            )
            return
    else:
        cols: dict[str, tuple[int, Column]] = {
            "UID": (
                0,
                Column(
                    "[bold white]UID",
                    footer=f"[white]{metadata_info['total_neurons']}[/white]",
                    style="white",
                    justify="right",
                    ratio=0.75,
                ),
            ),
            "GLOBAL_STAKE": (
                1,
                Column(
                    "[bold white]GLOBAL STAKE(\u03c4)",
                    footer=metadata_info["total_global_stake"],
                    style="bright_cyan",
                    justify="right",
                    no_wrap=True,
                    ratio=1.6,
                ),
            ),
            "LOCAL_STAKE": (
                2,
                Column(
                    f"[bold white]LOCAL STAKE({Balance.get_unit(netuid)})",
                    footer=metadata_info["total_local_stake"],
                    style="bright_green",
                    justify="right",
                    no_wrap=True,
                    ratio=1.5,
                ),
            ),
            "STAKE_WEIGHT": (
                3,
                Column(
                    f"[bold white]WEIGHT (\u03c4x{Balance.get_unit(netuid)})",
                    style="purple",
                    justify="right",
                    no_wrap=True,
                    ratio=1.3,
                ),
            ),
            "RANK": (
                4,
                Column(
                    "[bold white]RANK",
                    footer=metadata_info["rank"],
                    style="medium_purple",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "TRUST": (
                5,
                Column(
                    "[bold white]TRUST",
                    footer=metadata_info["trust"],
                    style="dark_sea_green",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "CONSENSUS": (
                6,
                Column(
                    "[bold white]CONSENSUS",
                    footer=metadata_info["consensus"],
                    style="rgb(42,161,152)",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "INCENTIVE": (
                7,
                Column(
                    "[bold white]INCENTIVE",
                    footer=metadata_info["incentive"],
                    style="#5fd7ff",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "DIVIDENDS": (
                8,
                Column(
                    "[bold white]DIVIDENDS",
                    footer=metadata_info["dividends"],
                    style="#8787d7",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "EMISSION": (
                9,
                Column(
                    "[bold white]EMISSION(\u03c1)",
                    footer=metadata_info["emission"],
                    style="#d7d7ff",
                    justify="right",
                    no_wrap=True,
                    ratio=1.5,
                ),
            ),
            "VTRUST": (
                10,
                Column(
                    "[bold white]VTRUST",
                    footer=metadata_info["validator_trust"],
                    style="magenta",
                    justify="right",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "VAL": (
                11,
                Column(
                    "[bold white]VAL",
                    justify="center",
                    style="bright_white",
                    no_wrap=True,
                    ratio=0.7,
                ),
            ),
            "UPDATED": (
                12,
                Column("[bold white]UPDATED", justify="right", no_wrap=True, ratio=1),
            ),
            "ACTIVE": (
                13,
                Column(
                    "[bold white]ACTIVE",
                    justify="center",
                    style="#8787ff",
                    no_wrap=True,
                    ratio=1,
                ),
            ),
            "AXON": (
                14,
                Column(
                    "[bold white]AXON",
                    justify="left",
                    style="dark_orange",
                    overflow="fold",
                    ratio=2,
                ),
            ),
            "HOTKEY": (
                15,
                Column(
                    "[bold white]HOTKEY",
                    justify="center",
                    style="bright_magenta",
                    overflow="fold",
                    ratio=1.5,
                ),
            ),
            "COLDKEY": (
                16,
                Column(
                    "[bold white]COLDKEY",
                    justify="center",
                    style="bright_magenta",
                    overflow="fold",
                    ratio=1.5,
                ),
            ),
        }
        table_cols: list[Column] = []
        table_cols_indices: list[int] = []
        for k, (idx, v) in cols.items():
            if display_cols[k] is True:
                table_cols_indices.append(idx)
                table_cols.append(v)

        table = Table(
            *table_cols,
            show_footer=True,
            show_edge=False,
            header_style="bold white",
            border_style="bright_black",
            style="bold",
            title_style="bold white",
            title_justify="center",
            show_lines=False,
            expand=True,
            title=(
                f"[underline dark_orange]Metagraph[/underline dark_orange]\n\n"
                f"Net: [bright_cyan]{metadata_info['net']}[/bright_cyan], "
                f"Block: [bright_cyan]{metadata_info['block']}[/bright_cyan], "
                f"N: [bright_green]{metadata_info['N0']}[/bright_green]/[bright_red]{metadata_info['N1']}[/bright_red], "
                f"Total Local Stake: [dark_orange]{metadata_info['total_local_stake']}[/dark_orange], "
                f"Issuance: [bright_blue]{metadata_info['issuance']}[/bright_blue], "
                f"Difficulty: [bright_cyan]{metadata_info['difficulty']}[/bright_cyan]\n"
            ),
            pad_edge=True,
        )

        if all(x is False for x in display_cols.values()):
            console.print("You have selected no columns to display in your config.")
            table.add_row(" " * 256)  # allows title to be printed
        elif any(x is False for x in display_cols.values()):
            console.print(
                "Limiting column display output based on your config settings. Hiding columns "
                f"{', '.join([k for (k, v) in display_cols.items() if v is False])}"
            )
            for row in table_data:
                new_row = [row[idx] for idx in table_cols_indices]
                table.add_row(*new_row)
        else:
            for row in table_data:
                table.add_row(*row)

        console.print(table)
