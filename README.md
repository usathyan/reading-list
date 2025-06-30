# 📚 GitHub Reading List Generator

> Transform your GitHub starred repositories into an organized, AI-powered reading list with beautiful visualizations.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌟 Overview

The GitHub Reading List Generator is an intelligent tool that analyzes your starred repositories and creates a comprehensive, categorized reading list. It combines GitHub API integration, AI-powered analysis, and beautiful data visualizations to help you organize and prioritize your learning journey.

## ✨ Features

### 🔍 **Intelligent Analysis**
- **AI-Powered Categorization**: Automatically groups repositories by technology, domain, and purpose
- **Content Analysis**: Extracts key information from README files and repository metadata
- **Trend Detection**: Identifies trending technologies and popular projects
- **Health Metrics**: Analyzes repository activity, maintenance status, and community engagement

### 📊 **Beautiful Visualizations**
- **Interactive Timeline**: Stars on X-axis (popularity) vs. Date on Y-axis (recency)
- **Category Clustering**: Visual grouping by technology and domain
- **Trend Analysis**: Star velocity and growth patterns
- **Export Options**: Multiple formats (JSON, CSV, HTML, SQLite)

### 🤖 **AI Integration**
- **OpenAI GPT**: Advanced content analysis and categorization
- **Anthropic Claude**: Alternative AI provider support
- **Custom Prompts**: Configurable analysis parameters
- **Smart Summarization**: Generates concise project descriptions

### 🔄 **Automation & Updates**
- **Auto-Refresh**: Scheduled updates via scripts
- **Incremental Updates**: Only processes new/changed repositories
- **Webhook Support**: Real-time updates (future feature)
- **CI/CD Integration**: Automated README generation

### 🎯 **Advanced Features**
- **Duplicate Detection**: Identifies similar or forked projects
- **Search & Filter**: Powerful querying capabilities
- **Bookmark Management**: Import/export bookmarks
- **Dashboard**: Interactive web interface
- **VSCode Integration**: Perfect for code exploration workflows

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- GitHub Personal Access Token
- OpenAI API Key (optional, for AI features)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/usathyan/reading-list.git
   cd reading-list
   ```

2. **Set up environment:**
   ```bash
   # Create virtual environment with uv
   uv venv --python 3.11
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e .
   ```

3. **Initialize configuration:**
   ```bash
   reading-list init
   ```

4. **Configure API keys:**
   ```bash
   # Edit .env file
   GITHUB_TOKEN=your_github_token_here
   OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

### Usage

#### Basic Commands

```bash
# Generate reading list
reading-list refresh

# Export data
reading-list export --format json --output my-reading-list.json

# Start web dashboard
reading-list serve --port 8000

# Show help
reading-list --help
```

#### Configuration

Edit `config.yaml` to customize:

```yaml
github:
  username: "your-username"
  rate_limit: 5000
  
ai:
  provider: "openai"  # or "anthropic"
  model: "gpt-4"
  max_tokens: 1000
  
visualization:
  theme: "dark"
  format: "html"
  interactive: true
  
output:
  formats: ["json", "html", "csv"]
  readme_template: "templates/README_template.md"
```

## 📁 Project Structure

```
reading-list/
├── src/reading_list/           # Main package
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   ├── pipeline.py             # Main processing pipeline
│   ├── github_client.py        # GitHub API integration
│   ├── ai_analyzer.py          # AI analysis components
│   ├── visualizations.py       # Data visualization
│   ├── content_generator.py    # README generation
│   ├── config.py              # Configuration management
│   └── scripts/               # Utility scripts
├── tests/                     # Test suite
├── data/                      # Generated data
├── docs/                      # Documentation
├── scripts/                   # Shell scripts
├── config.yaml               # Main configuration
└── README.md                 # This file
```

## 🔧 Configuration Options

### GitHub Settings
- `github.username`: Your GitHub username
- `github.rate_limit`: API rate limit (requests per hour)
- `github.cache_ttl`: Cache duration in seconds

### AI Analysis
- `ai.provider`: AI service provider ("openai" or "anthropic")
- `ai.model`: Model name (e.g., "gpt-4", "claude-3-sonnet")
- `ai.temperature`: Creativity level (0.0-1.0)
- `ai.max_tokens`: Maximum response length

### Visualization
- `visualization.theme`: Color theme ("light", "dark", "auto")
- `visualization.format`: Output format ("html", "png", "svg")
- `visualization.interactive`: Enable interactive features

### Output
- `output.formats`: Export formats to generate
- `output.readme_template`: Template file for README generation
- `output.data_dir`: Directory for generated data

## 🎨 Visualization Examples

### Star Timeline
```python
# Generated visualization showing:
# - X-axis: Repository stars (popularity)
# - Y-axis: Date starred (recency)
# - Color: Category/technology
# - Size: Repository activity level
```

### Category Distribution
```python
# Pie chart or treemap showing:
# - Distribution of repositories by category
# - Technology stack popularity
# - Language usage patterns
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📊 Roadmap

### v0.2.0 - Enhanced Analysis
- [ ] Advanced AI categorization algorithms
- [ ] Repository health scoring
- [ ] Trend analysis and predictions
- [ ] Integration with more AI providers

### v0.3.0 - Web Dashboard
- [ ] Interactive web interface
- [ ] Real-time updates
- [ ] Collaborative features
- [ ] Social sharing capabilities

### v0.4.0 - Advanced Features
- [ ] Webhook integration
- [ ] API for third-party integrations
- [ ] Mobile app
- [ ] Enterprise features

## 🔍 Related Projects

- [github-stars-manager](https://github.com/example/github-stars-manager): Web-based tagging system
- [starghaze](https://github.com/example/starghaze): Export to various formats with analysis
- [starred-repos-collection](https://github.com/example/starred-repos-collection): Auto-categorization
- [Awesome-Starred](https://github.com/example/awesome-starred): Simple README generation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GitHub API for providing comprehensive repository data
- OpenAI and Anthropic for AI analysis capabilities
- Plotly for interactive visualizations
- The open-source community for inspiration and tools

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/usathyan/reading-list/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/usathyan/reading-list/discussions)
- 📖 Documentation: [Wiki](https://github.com/usathyan/reading-list/wiki)

---

**Made with ❤️ by developers, for developers** 