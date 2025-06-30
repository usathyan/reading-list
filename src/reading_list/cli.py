"""Command-line interface for GitHub Reading List Generator."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import Config, load_config
from .pipeline import Pipeline
from .version import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path], debug: bool) -> None:
    """GitHub Reading List Generator CLI
    
    Transform your GitHub starred repositories into an organized,
    AI-powered reading list with beautiful visualizations.
    """
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    
    # Load configuration
    config_path = config or Path("config.yaml")
    try:
        ctx.obj["config"] = load_config(config_path)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--force", 
    is_flag=True, 
    help="Force refresh even if cache is valid"
)
@click.option(
    "--no-ai", 
    is_flag=True, 
    help="Skip AI analysis"
)
@click.pass_context
def refresh(ctx: click.Context, force: bool, no_ai: bool) -> None:
    """Refresh the reading list data from GitHub."""
    config: Config = ctx.obj["config"]
    
    console.print(Panel.fit(
        "🔄 [bold blue]Refreshing Reading List[/bold blue]",
        border_style="blue"
    ))
    
    # Validate GitHub token
    if not config.github.token:
        console.print("[red]GitHub token not found. Please set GITHUB_TOKEN environment variable.[/red]")
        sys.exit(1)
    
    # Run the pipeline
    pipeline = Pipeline(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing...", total=None)
        
        try:
            # Run async pipeline
            result = asyncio.run(pipeline.run(force_refresh=force, skip_ai=no_ai))
            
            progress.update(task, description="Complete!")
            
            # Display results
            table = Table(title="📊 Processing Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Repositories Processed", str(result.total_repositories))
            table.add_row("Categories Found", str(result.total_categories))
            table.add_row("Visualizations Generated", str(result.visualizations_count))
            table.add_row("Export Formats", str(result.export_formats_count))
            
            console.print(table)
            
            console.print(f"\n[green]✅ Reading list updated successfully![/green]")
            console.print(f"[blue]📄 Output saved to: {result.output_path}[/blue]")
            
        except Exception as e:
            progress.update(task, description="Failed!")
            console.print(f"[red]❌ Error during refresh: {e}[/red]")
            if ctx.obj["debug"]:
                import traceback
                console.print(traceback.format_exc())
            sys.exit(1)


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv", "html", "markdown"]),
    default="json",
    help="Export format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path",
)
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty-print JSON output",
)
@click.pass_context
def export(ctx: click.Context, format: str, output: Optional[Path], pretty: bool) -> None:
    """Export reading list data in various formats."""
    config: Config = ctx.obj["config"]
    
    console.print(Panel.fit(
        f"📤 [bold green]Exporting to {format.upper()}[/bold green]",
        border_style="green"
    ))
    
    # Determine output path
    if not output:
        output = Path(f"reading_list.{format}")
    
    try:
        pipeline = Pipeline(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Exporting to {format}...", total=None)
            
            # Export data
            result = asyncio.run(pipeline.export(format, output, pretty_json=pretty))
            
            progress.update(task, description="Complete!")
            
        console.print(f"[green]✅ Data exported successfully![/green]")
        console.print(f"[blue]📄 File saved to: {output}[/blue]")
        console.print(f"[blue]📊 Records exported: {result.record_count}[/blue]")
        
    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")
        if ctx.obj["debug"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option(
    "--host",
    default="localhost",
    help="Host to bind the server to",
)
@click.option(
    "--port",
    default=8000,
    help="Port to bind the server to",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool) -> None:
    """Start the web dashboard server."""
    config: Config = ctx.obj["config"]
    
    console.print(Panel.fit(
        f"🌐 [bold magenta]Starting Web Dashboard[/bold magenta]",
        border_style="magenta"
    ))
    
    try:
        import uvicorn
        from .dashboard import create_app
        
        app = create_app(config)
        
        console.print(f"[green]🚀 Server starting on http://{host}:{port}[/green]")
        console.print("[yellow]Press Ctrl+C to stop the server[/yellow]")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info" if not ctx.obj["debug"] else "debug",
        )
        
    except ImportError:
        console.print("[red]❌ Web dashboard dependencies not installed.[/red]")
        console.print("[yellow]Install with: pip install 'reading-list[web]'[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Server failed to start: {e}[/red]")
        if ctx.obj["debug"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option(
    "--username",
    prompt="GitHub username",
    help="Your GitHub username",
)
@click.option(
    "--token",
    help="GitHub personal access token (optional, can be set via environment)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing configuration",
)
@click.pass_context
def init(ctx: click.Context, username: str, token: Optional[str], force: bool) -> None:
    """Initialize configuration files and directories."""
    console.print(Panel.fit(
        "🎯 [bold cyan]Initializing Reading List Generator[/bold cyan]",
        border_style="cyan"
    ))
    
    config_path = Path("config.yaml")
    env_path = Path(".env")
    
    # Check if files exist
    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration file already exists: {config_path}[/yellow]")
        if not click.confirm("Overwrite existing configuration?"):
            sys.exit(0)
    
    try:
        # Create directories
        directories = [
            "data",
            "data/cache",
            "data/exports", 
            "data/logs",
            "templates",
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
        # Create .env file
        env_content = f"""# GitHub Reading List Generator Environment Variables

# GitHub Configuration
GITHUB_TOKEN={token or 'your_github_token_here'}
GITHUB_USERNAME={username}

# AI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/reading_list.db
"""
        
        env_path.write_text(env_content)
        
        # Update config.yaml with username
        config = load_config()
        config.github.username = username
        
        # Save updated config
        import yaml
        with open(config_path, "w") as f:
            yaml.dump(config.dict(), f, default_flow_style=False, indent=2)
        
        console.print("[green]✅ Configuration initialized successfully![/green]")
        console.print(f"[blue]📄 Configuration file: {config_path}[/blue]")
        console.print(f"[blue]🔑 Environment file: {env_path}[/blue]")
        
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit .env file and add your GitHub token")
        console.print("2. Optionally add AI API keys for enhanced analysis")
        console.print("3. Run 'reading-list refresh' to generate your reading list")
        
    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        if ctx.obj["debug"]:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current status and configuration."""
    config: Config = ctx.obj["config"]
    
    console.print(Panel.fit(
        "📊 [bold blue]Reading List Status[/bold blue]",
        border_style="blue"
    ))
    
    # Configuration status
    config_table = Table(title="⚙️ Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", style="yellow")
    
    # GitHub config
    github_token_status = "✅ Set" if config.github.token else "❌ Missing"
    config_table.add_row("GitHub Username", config.github.username, "✅ OK")
    config_table.add_row("GitHub Token", "***" if config.github.token else "Not set", github_token_status)
    
    # AI config
    ai_status = "✅ Enabled" if config.ai.provider != "none" else "❌ Disabled"
    config_table.add_row("AI Provider", config.ai.provider, ai_status)
    
    console.print(config_table)
    
    # File system status
    fs_table = Table(title="📁 File System")
    fs_table.add_column("Path", style="cyan")
    fs_table.add_column("Status", style="green")
    fs_table.add_column("Size", style="yellow")
    
    paths_to_check = [
        Path("data"),
        Path("data/cache"),
        Path("data/exports"),
        Path("data/logs"),
        Path("data/reading_list.db"),
    ]
    
    for path in paths_to_check:
        if path.exists():
            if path.is_dir():
                size = f"{len(list(path.iterdir()))} items"
            else:
                size = f"{path.stat().st_size} bytes"
            status = "✅ Exists"
        else:
            size = "-"
            status = "❌ Missing"
        
        fs_table.add_row(str(path), status, size)
    
    console.print(fs_table)


def main():
    """Entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    cli() 