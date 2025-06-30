"""Refresh script wrapper for GitHub Reading List Generator."""

import asyncio
import sys
from pathlib import Path

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reading_list.config import load_config
from reading_list.pipeline import Pipeline


async def main():
    """Main refresh function."""
    try:
        # Load configuration
        config = load_config()
        
        # Create and run pipeline
        pipeline = Pipeline(config)
        result = await pipeline.run()
        
        print(f"✅ Refresh completed successfully!")
        print(f"📊 Processed {result.total_repositories} repositories")
        print(f"📂 Output saved to: {result.output_path}")
        
    except Exception as e:
        print(f"❌ Refresh failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 