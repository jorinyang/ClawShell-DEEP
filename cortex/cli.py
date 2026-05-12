"""ClawShell 2.0 — CLI"""
import asyncio
from pathlib import Path
from typing import Optional
import typer

app = typer.Typer(
    name="clawshell",
    help="ClawShell 2.0 — Distributed Neural Architecture",
)


@app.command()
def cortex(
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
    port: int = typer.Option(9000, "--port", "-p"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """Start cortex (main brain)"""
    from cortex.main import main
    asyncio.run(main())


@app.command()
def ganglion(
    node_id: str = typer.Option("", "--id"),
    cortex_host: str = typer.Option("localhost", "--cortex-host"),
    cortex_port: int = typer.Option(9000, "--cortex-port"),
    offline: bool = typer.Option(False, "--offline"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """Start ganglion (edge brain)"""
    from ganglion.main import main
    asyncio.run(main())


@app.command()
def version():
    """Show version"""
    typer.echo("ClawShell 2.0.0 — DEEP")


@app.command()
def init(
    mode: str = typer.Option("ganglion", "--mode", "-m"),
    output: Path = typer.Option(Path("config"), "--output", "-o"),
):
    """Generate config files"""
    import yaml
    output.mkdir(parents=True, exist_ok=True)
    if mode == "cortex":
        cfg = {
            "node_id": "cortex-01",
            "host": "0.0.0.0",
            "port": 9000,
            "strategy": "default",
            "heartbeat_interval": 30,
        }
        f = output / "cortex.yaml"
    else:
        cfg = {
            "node_id": "",
            "cortex_host": "localhost",
            "cortex_port": 9000,
            "strategy": "default",
            "heartbeat_interval": 30,
            "perception_interval": 60,
            "auto_register": True,
            "offline_mode": False,
        }
        f = output / "ganglion.yaml"
    with open(f, "w", encoding="utf-8") as fh:
        yaml.dump(cfg, fh, allow_unicode=True, default_flow_style=False)
    typer.echo(f"Config generated: {f}")


def main():
    app()


if __name__ == "__main__":
    main()
