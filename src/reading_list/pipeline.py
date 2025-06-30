"""Main processing pipeline for GitHub Reading List Generator."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import Config
from .github_client import GitHubClient, Repository

logger = logging.getLogger(__name__)


class ProcessingResult:
    """Result of the processing pipeline."""
    
    def __init__(
        self,
        total_repositories: int = 0,
        total_categories: int = 0,
        visualizations_count: int = 0,
        export_formats_count: int = 0,
        output_path: Optional[Path] = None,
    ):
        self.total_repositories = total_repositories
        self.total_categories = total_categories
        self.visualizations_count = visualizations_count
        self.export_formats_count = export_formats_count
        self.output_path = output_path
        self.completed_at = datetime.now()


class ExportResult:
    """Result of the export operation."""
    
    def __init__(self, record_count: int = 0, output_path: Optional[Path] = None):
        self.record_count = record_count
        self.output_path = output_path
        self.completed_at = datetime.now()


class Pipeline:
    """Main processing pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.github_client = GitHubClient(config.github)
        
        # Setup logging
        self._setup_logging()
        
        logger.info("Pipeline initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level),
            format=self.config.logging.format,
        )
    
    async def run(
        self, 
        force_refresh: bool = False, 
        skip_ai: bool = False
    ) -> ProcessingResult:
        """Run the complete pipeline."""
        logger.info("Starting pipeline execution")
        
        try:
            # Step 1: Fetch repositories
            logger.info("Fetching starred repositories from GitHub")
            repositories = await self._fetch_repositories()
            logger.info(f"Found {len(repositories)} starred repositories")
            
            # Step 2: AI Analysis (if enabled and not skipped)
            if self.config.features.enable_ai_analysis and not skip_ai:
                logger.info("Analyzing repositories with AI")
                analysis_result = await self._analyze_repositories(repositories)
                logger.info("AI analysis completed")
            else:
                logger.info("Skipping AI analysis")
                analysis_result = self._create_basic_analysis(repositories)
            
            # Step 3: Generate visualizations (if enabled)
            visualizations_count = 0
            if self.config.features.enable_visualizations:
                logger.info("Generating visualizations")
                visualizations_count = await self._generate_visualizations(repositories)
                logger.info(f"Generated {visualizations_count} visualizations")
            
            # Step 4: Generate content and exports
            logger.info("Generating content and exports")
            export_count = await self._generate_content_and_exports(repositories, analysis_result)
            logger.info(f"Generated {export_count} export formats")
            
            # Create result
            result = ProcessingResult(
                total_repositories=len(repositories),
                total_categories=len(analysis_result.get("categories", {})),
                visualizations_count=visualizations_count,
                export_formats_count=export_count,
                output_path=Path(self.config.output.data_dir),
            )
            
            logger.info("Pipeline execution completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise
    
    async def _fetch_repositories(self) -> List[Repository]:
        """Fetch starred repositories from GitHub."""
        repositories = []
        
        async for repo in self.github_client.get_starred_repositories(
            self.config.github.username
        ):
            repositories.append(repo)
            
            # Log progress every 50 repositories
            if len(repositories) % 50 == 0:
                logger.info(f"Fetched {len(repositories)} repositories so far...")
        
        return repositories
    
    def _create_basic_analysis(self, repositories: List[Repository]) -> dict:
        """Create basic analysis without AI."""
        # Simple categorization by language
        categories = {}
        for repo in repositories:
            language = repo.language or "Unknown"
            if language not in categories:
                categories[language] = []
            categories[language].append(repo)
        
        return {
            "categories": categories,
            "summary": f"Analyzed {len(repositories)} repositories",
            "method": "basic",
        }
    
    async def _analyze_repositories(self, repositories: List[Repository]) -> dict:
        """Analyze repositories using AI (placeholder)."""
        # This would integrate with AI providers
        logger.info("AI analysis is not yet implemented - using basic analysis")
        return self._create_basic_analysis(repositories)
    
    async def _generate_visualizations(self, repositories: List[Repository]) -> int:
        """Generate visualizations (placeholder)."""
        # This would create Plotly charts
        logger.info("Visualization generation is not yet implemented")
        return 0
    
    async def _generate_content_and_exports(
        self, 
        repositories: List[Repository], 
        analysis_result: dict
    ) -> int:
        """Generate content and export in various formats."""
        export_count = 0
        
        # Generate basic README
        readme_content = self._generate_basic_readme(repositories, analysis_result)
        readme_path = Path(self.config.output.data_dir) / "README.md"
        readme_path.write_text(readme_content)
        export_count += 1
        
        logger.info(f"Generated README at {readme_path}")
        
        return export_count
    
    def _generate_basic_readme(
        self, 
        repositories: List[Repository], 
        analysis_result: dict
    ) -> str:
        """Generate a basic README file."""
        content = f"""# 📚 My GitHub Reading List

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Summary

- **Total Repositories**: {len(repositories)}
- **Categories**: {len(analysis_result.get('categories', {}))}

## 📋 Repositories by Category

"""
        
        # Add repositories by category
        categories = analysis_result.get("categories", {})
        for category, repos in categories.items():
            content += f"\n### {category} ({len(repos)} repositories)\n\n"
            
            for repo in repos[:10]:  # Limit to first 10 per category
                stars = "⭐" * min(5, repo.stargazers_count // 1000)
                content += f"- **[{repo.name}]({repo.html_url})**{stars}\n"
                if repo.description:
                    content += f"  {repo.description}\n"
                content += f"  *{repo.stargazers_count:,} stars • {repo.language or 'Unknown'}*\n\n"
            
            if len(repos) > 10:
                content += f"  ... and {len(repos) - 10} more repositories\n\n"
        
        content += f"""
---

*Generated by [GitHub Reading List Generator](https://github.com/usathyan/reading-list)*
"""
        
        return content
    
    async def export(
        self, 
        format_type: str, 
        output_path: Path, 
        pretty_json: bool = False
    ) -> ExportResult:
        """Export data in specified format."""
        logger.info(f"Exporting data to {format_type} format")
        
        # Fetch repositories
        repositories = await self._fetch_repositories()
        
        if format_type == "json":
            import json
            
            data = [repo.dict() for repo in repositories]
            
            with open(output_path, "w") as f:
                if pretty_json:
                    json.dump(data, f, indent=2, default=str)
                else:
                    json.dump(data, f, default=str)
        
        elif format_type == "csv":
            import csv
            
            with open(output_path, "w", newline="") as f:
                if repositories:
                    writer = csv.DictWriter(f, fieldnames=repositories[0].dict().keys())
                    writer.writeheader()
                    for repo in repositories:
                        # Convert datetime objects to strings
                        row = {k: str(v) if hasattr(v, 'isoformat') else v 
                               for k, v in repo.dict().items()}
                        writer.writerow(row)
        
        elif format_type == "markdown":
            content = self._generate_basic_readme(
                repositories, 
                self._create_basic_analysis(repositories)
            )
            output_path.write_text(content)
        
        elif format_type == "html":
            # Basic HTML export
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>GitHub Reading List</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .repo {{ margin: 20px 0; padding: 10px; border-left: 3px solid #0366d6; }}
        .repo-name {{ font-size: 18px; font-weight: bold; }}
        .repo-desc {{ color: #586069; margin: 5px 0; }}
        .repo-meta {{ font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <h1>📚 GitHub Reading List</h1>
    <p>Total repositories: {len(repositories)}</p>
"""
            
            for repo in repositories:
                html_content += f"""
    <div class="repo">
        <div class="repo-name">
            <a href="{repo.html_url}" target="_blank">{repo.name}</a>
        </div>
        <div class="repo-desc">{repo.description or 'No description'}</div>
        <div class="repo-meta">
            ⭐ {repo.stargazers_count:,} stars • 
            {repo.language or 'Unknown'} • 
            Updated: {repo.updated_at.strftime('%Y-%m-%d') if repo.updated_at else 'Unknown'}
        </div>
    </div>
"""
            
            html_content += """
</body>
</html>
"""
            output_path.write_text(html_content)
        
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        result = ExportResult(
            record_count=len(repositories),
            output_path=output_path,
        )
        
        logger.info(f"Export completed: {result.record_count} records to {output_path}")
        return result 