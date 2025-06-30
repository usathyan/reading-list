"""Configuration management for GitHub Reading List Generator."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GitHubConfig(BaseModel):
    """GitHub API configuration."""
    username: str = "your-username"
    token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    base_url: str = "https://api.github.com"
    rate_limit: int = 5000
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    cache_ttl: int = 3600
    enable_cache: bool = True


class OpenAIConfig(BaseModel):
    """OpenAI API configuration."""
    api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.3
    base_url: str = "https://api.openai.com/v1"


class AnthropicConfig(BaseModel):
    """Anthropic API configuration."""
    api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1000
    temperature: float = 0.3


class AIConfig(BaseModel):
    """AI analysis configuration."""
    provider: str = "openai"  # "openai", "anthropic", or "none"
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    enable_content_analysis: bool = True
    enable_categorization: bool = True
    enable_summarization: bool = True
    batch_size: int = 10


class TimelineConfig(BaseModel):
    """Timeline visualization configuration."""
    x_axis: str = "stars"
    y_axis: str = "starred_date"
    color_by: str = "category"
    size_by: str = "activity"
    show_trends: bool = True


class CategoryConfig(BaseModel):
    """Category visualization configuration."""
    chart_type: str = "treemap"
    min_repos: int = 2
    max_categories: int = 15


class VisualizationConfig(BaseModel):
    """Visualization configuration."""
    theme: str = "dark"
    formats: List[str] = Field(default_factory=lambda: ["html", "png", "svg"])
    interactive: bool = True
    width: int = 1200
    height: int = 800
    timeline: TimelineConfig = Field(default_factory=TimelineConfig)
    categories: CategoryConfig = Field(default_factory=CategoryConfig)


class ReadmeConfig(BaseModel):
    """README generation configuration."""
    template: str = "templates/README_template.md"
    filename: str = "READING_LIST.md"
    include_visualizations: bool = True
    include_stats: bool = True
    group_by_category: bool = True


class ExportConfig(BaseModel):
    """Export configuration."""
    include_metadata: bool = True
    pretty_json: bool = True
    csv_delimiter: str = ","


class OutputConfig(BaseModel):
    """Output configuration."""
    data_dir: str = "data"
    formats: List[str] = Field(default_factory=lambda: ["json", "csv", "html", "markdown"])
    readme: ReadmeConfig = Field(default_factory=ReadmeConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)


class DatabaseConfig(BaseModel):
    """Database configuration."""
    path: str = "data/reading_list.db"
    timeout: int = 30
    check_same_thread: bool = False
    vacuum_on_startup: bool = False
    backup_frequency: str = "weekly"


class LogFileConfig(BaseModel):
    """Log file configuration."""
    application: str = "data/logs/application.log"
    github_api: str = "data/logs/github_api.log"
    ai_analysis: str = "data/logs/ai_analysis.log"


class ConsoleConfig(BaseModel):
    """Console logging configuration."""
    enabled: bool = True
    level: str = "INFO"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    files: LogFileConfig = Field(default_factory=LogFileConfig)
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    console: ConsoleConfig = Field(default_factory=ConsoleConfig)


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    max_concurrent_requests: int = 10
    max_concurrent_analysis: int = 5
    batch_size: int = 100
    cache_size: int = 1000
    max_memory_mb: int = 1024
    request_delay: float = 0.1


class FeatureConfig(BaseModel):
    """Feature flags configuration."""
    enable_ai_analysis: bool = True
    enable_visualizations: bool = True
    enable_web_dashboard: bool = False
    enable_real_time_updates: bool = False
    enable_social_features: bool = False


class CategorizationConfig(BaseModel):
    """Categorization rules configuration."""
    languages: Dict[str, List[str]] = Field(default_factory=lambda: {
        "Web Development": ["JavaScript", "TypeScript", "HTML", "CSS", "PHP", "Ruby"],
        "Systems Programming": ["C", "C++", "Rust", "Go", "Zig"],
        "Data Science": ["Python", "R", "Julia", "Scala"],
        "Mobile Development": ["Swift", "Kotlin", "Dart", "Objective-C"],
        "Functional Programming": ["Haskell", "Elixir", "Erlang", "OCaml", "F#"],
    })
    topics: Dict[str, List[str]] = Field(default_factory=lambda: {
        "Machine Learning": ["machine-learning", "deep-learning", "neural-networks", "ai"],
        "Web Development": ["web", "frontend", "backend", "fullstack", "api"],
        "DevOps": ["docker", "kubernetes", "ci-cd", "deployment", "infrastructure"],
        "Security": ["security", "cryptography", "penetration-testing", "vulnerability"],
        "Database": ["database", "sql", "nosql", "orm", "migration"],
    })
    custom_rules: Dict[str, List[str]] = Field(default_factory=lambda: {
        "CLI Tools": ["cli", "command-line", "terminal", "shell"],
        "Testing": ["test", "testing", "unit-test", "integration-test"],
        "Documentation": ["docs", "documentation", "wiki", "guide"],
    })


class TemplateVariables(BaseModel):
    """Template variables configuration."""
    author: str = "Reading List Generator"
    generated_date: str = "{{ now }}"
    total_repositories: str = "{{ stats.total_repos }}"


class TemplateConfig(BaseModel):
    """Template configuration."""
    directory: str = "templates"
    readme: str = "README_template.md"
    html_report: str = "report_template.html"
    variables: TemplateVariables = Field(default_factory=TemplateVariables)


class Config(BaseSettings):
    """Main configuration class."""
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    categorization: CategorizationConfig = Field(default_factory=CategorizationConfig)
    templates: TemplateConfig = Field(default_factory=TemplateConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load environment variables into nested configs
        self._load_env_vars()

    def _load_env_vars(self):
        """Load environment variables into configuration."""
        # GitHub token
        if github_token := os.getenv("GITHUB_TOKEN"):
            self.github.token = github_token

        # GitHub username
        if github_username := os.getenv("GITHUB_USERNAME"):
            self.github.username = github_username

        # OpenAI API key
        if openai_key := os.getenv("OPENAI_API_KEY"):
            self.ai.openai.api_key = openai_key

        # Anthropic API key
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            self.ai.anthropic.api_key = anthropic_key

    def validate_required_settings(self) -> List[str]:
        """Validate required settings and return list of missing items."""
        missing = []

        # GitHub token is required
        if not self.github.token:
            missing.append("GITHUB_TOKEN environment variable")

        # GitHub username is required
        if not self.github.username or self.github.username == "your-username":
            missing.append("GitHub username")

        # AI provider validation
        if self.ai.provider == "openai" and not self.ai.openai.api_key:
            missing.append("OPENAI_API_KEY environment variable (or set ai.provider to 'none')")
        elif self.ai.provider == "anthropic" and not self.ai.anthropic.api_key:
            missing.append("ANTHROPIC_API_KEY environment variable (or set ai.provider to 'none')")

        return missing

    def create_directories(self):
        """Create necessary directories."""
        directories = [
            Path(self.output.data_dir),
            Path(self.output.data_dir) / "cache",
            Path(self.output.data_dir) / "exports",
            Path(self.output.data_dir) / "logs",
            Path(self.templates.directory),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file and environment variables."""
    config_data = {}

    # Load from YAML file if exists
    if config_path is None:
        config_path = Path("config.yaml")
    else:
        config_path = Path(config_path)

    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

    # Create config instance
    config = Config(**config_data)

    # Validate required settings
    missing = config.validate_required_settings()
    if missing:
        print(f"Warning: Missing required configuration: {', '.join(missing)}")

    # Create directories
    config.create_directories()

    return config


def create_default_config(output_path: Union[str, Path] = "config.yaml") -> None:
    """Create a default configuration file."""
    config = Config()
    output_path = Path(output_path)

    # Convert to dict and save as YAML
    config_dict = config.dict()

    with open(output_path, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)

    print(f"Default configuration created at: {output_path}")


if __name__ == "__main__":
    # Create default config for testing
    create_default_config() 