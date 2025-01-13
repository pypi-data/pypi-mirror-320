"""Main application logic."""

from typing import Optional, List, Dict, Any
import json
import logging
import os
import time
import platform
from pathlib import Path
from datetime import datetime

from playwright.async_api import Error as PlaywrightError
from rag_retriever.crawling.playwright_crawler import PlaywrightCrawler
from rag_retriever.crawling.exceptions import PageLoadError, ContentExtractionError
from rag_retriever.search.searcher import Searcher
from rag_retriever.vectorstore.store import VectorStore, get_vectorstore_path
from rag_retriever.utils.config import config, mask_api_key

logger = logging.getLogger(__name__)

# Maximum number of retries for recoverable errors
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 2


def get_system_info() -> Dict[str, str]:
    """Get system information for diagnostics."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "memory": (
            os.popen("free -h").readlines()[1].split()[1]
            if platform.system() == "Linux"
            else "N/A"
        ),
    }


def process_url(url: str, max_depth: int = 2, verbose: bool = True) -> int:
    """Process a URL, extracting and indexing its content."""
    start_time = time.time()
    crawl_stats = {
        "pages_attempted": 0,
        "pages_successful": 0,
        "pages_failed": 0,
        "total_content_size": 0,
        "retry_count": 0,
        "errors": {},
    }

    # Set logging levels based on verbose mode
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("chromadb").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)

        # System diagnostics
        sys_info = get_system_info()
        logger.info("\nSystem Information:")
        for key, value in sys_info.items():
            logger.info(f"- {key}: {value}")

        # Log configuration
        logger.info("\nStarting content fetch and indexing process...")
        logger.info("Configuration:")
        logger.info("- URL: %s", url)
        logger.info("- Max depth: %d", max_depth)
        logger.info("- Vector store: %s", get_vectorstore_path())
        logger.info("- Model: %s", config.vector_store["embedding_model"])
        logger.info("- API key: %s", mask_api_key(os.getenv("OPENAI_API_KEY", "")))
        logger.info("- Config file: %s", config.config_path)
        logger.info("- Environment file: %s", config.env_path)

        # Browser configuration
        logger.info("\nBrowser configuration:")
        logger.info("- Headless mode: %s", config.browser["launch_options"]["headless"])
        logger.info(
            "- Browser channel: %s",
            config.browser["launch_options"].get("channel", "default"),
        )
        logger.info("- Wait time: %d seconds", config.browser["wait_time"])
        logger.info(
            "- Viewport: %dx%d",
            config.browser["viewport"]["width"],
            config.browser["viewport"]["height"],
        )

    try:
        logger.info("\nInitializing browser...")
        crawler = PlaywrightCrawler()
        store = VectorStore()

        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Use the synchronous wrapper for the async crawler
                logger.info("Starting crawl operation...")
                documents = crawler.run_crawl(url, max_depth=max_depth)

                # Update statistics
                crawl_stats["pages_successful"] = len(documents)
                crawl_stats["total_content_size"] = sum(
                    len(doc.page_content) for doc in documents
                )

                if verbose:
                    logger.info("\nCrawl statistics:")
                    logger.info(
                        "- Pages processed successfully: %d",
                        crawl_stats["pages_successful"],
                    )
                    logger.info(
                        "- Total content size: %.2f KB",
                        crawl_stats["total_content_size"] / 1024,
                    )
                    logger.info(
                        "- Average content size: %.2f KB",
                        (
                            crawl_stats["total_content_size"] / len(documents) / 1024
                            if documents
                            else 0
                        ),
                    )
                    logger.info(
                        "- Crawl duration: %.2f seconds", time.time() - start_time
                    )
                    logger.info(
                        "- Pages/second: %.2f",
                        len(documents) / (time.time() - start_time) if documents else 0,
                    )
                    if crawl_stats["retry_count"]:
                        logger.info("- Retry attempts: %d", crawl_stats["retry_count"])
                        logger.info(
                            "- Error types encountered: %s",
                            ", ".join(crawl_stats["errors"].keys()),
                        )

                logger.info("\nIndexing documents...")
                store.add_documents(documents)
                logger.info("Indexing complete.")

                return 0

            except (PageLoadError, PlaywrightError) as e:
                retry_count += 1
                crawl_stats["retry_count"] += 1
                error_type = e.__class__.__name__
                crawl_stats["errors"][error_type] = (
                    crawl_stats["errors"].get(error_type, 0) + 1
                )

                if retry_count < MAX_RETRIES:
                    logger.warning(f"Attempt {retry_count} failed: {str(e)}")
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY * retry_count)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
                    if isinstance(
                        e, PlaywrightError
                    ) and "Chromium revision is not downloaded" in str(e):
                        logger.error(
                            "Try running 'playwright install chromium' to install required browser."
                        )
                    return 1

            except ContentExtractionError as e:
                logger.error("Failed to extract content: %s", str(e))
                crawl_stats["errors"]["ContentExtractionError"] = (
                    crawl_stats["errors"].get("ContentExtractionError", 0) + 1
                )
                return 1

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        crawl_stats["errors"]["UnexpectedError"] = (
            crawl_stats["errors"].get("UnexpectedError", 0) + 1
        )
        return 1

    finally:
        if "crawler" in locals():
            logger.debug("Cleaning up browser resources...")
            if verbose:
                logger.info("\nFinal Statistics:")
                logger.info(
                    "- Total execution time: %.2f seconds", time.time() - start_time
                )
                logger.info(
                    "- Memory usage: %s",
                    (
                        os.popen("ps -o rss= -p %d" % os.getpid()).read().strip()
                        if platform.system() != "Windows"
                        else "N/A"
                    ),
                )
                if crawl_stats["errors"]:
                    logger.info("- Error summary:")
                    for error_type, count in crawl_stats["errors"].items():
                        logger.info(f"  - {error_type}: {count} occurrences")


def search_content(
    query: str,
    limit: Optional[int] = None,
    score_threshold: Optional[float] = None,
    full_content: bool = False,
    json_output: bool = False,
    verbose: bool = False,
) -> int:
    """Search indexed content."""
    # Use default values from config if not specified
    if limit is None:
        limit = config.search["default_limit"]
    if score_threshold is None:
        score_threshold = config.search["default_score_threshold"]

    # Set logging levels based on verbose mode
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("chromadb").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)
        # Log configuration
        logger.info("\nStarting content search...")
        logger.info("Configuration:")
        logger.info("- Query: %s", query)
        logger.info("- Result limit: %d", limit)
        logger.info("- Score threshold: %.2f", score_threshold)
        logger.info("- Vector store: %s", get_vectorstore_path())
        logger.info("- Model: %s", config.vector_store["embedding_model"])
        logger.info("- API key: %s", mask_api_key(os.getenv("OPENAI_API_KEY", "")))
        logger.info("- Config file: %s", config.config_path)
        logger.info("- Environment file: %s", config.env_path)

    try:
        searcher = Searcher()
        results = searcher.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
        )

        if not results:
            if verbose:
                logger.info("\nNo results found matching the query.")
            return 0

        if json_output:
            print(
                json.dumps([searcher.format_result_json(r) for r in results], indent=2)
            )
        else:
            if verbose:
                print("\nSearch Results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {searcher.format_result(result, show_full=full_content)}")

        return 0
    except Exception as e:
        logger.error("Error searching content: %s", str(e))
        return 1
