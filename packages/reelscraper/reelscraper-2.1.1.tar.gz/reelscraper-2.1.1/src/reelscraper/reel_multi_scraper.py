import concurrent.futures
from typing import List, Dict, Optional
from reelscraper.utils import LoggerManager, AccountManager, DataSaver
from reelscraper import ReelScraper


class ReelMultiScraper:
    """
    [ReelMultiScraper] retrieves reels for multiple Instagram accounts in parallel using [ReelScraper].

    :param [accounts_file]: Path to a text file containing one username per line
    :param [scraper]: Instance of [ReelScraper] used to fetch reels
    :param [max_workers]: Maximum number of threads to use for concurrent requests
    """

    def __init__(
        self,
        scraper: ReelScraper,
        max_workers: int = 5,
        data_saver: Optional[DataSaver] = None,
    ) -> None:
        """
        Initializes [MultiAccountScraper] by loading account names and storing references.

        :param [accounts_file]: Path to a text file containing one username per line
        :param [scraper]: Instance of [ReelScraper] used to fetch reels
        :param [max_workers]: Maximum number of threads to use for concurrent requests
        """
        self.scraper: ReelScraper = scraper
        self.max_workers: int = max_workers
        self.data_saver: Optional[DataSaver] = data_saver

    def scrape_accounts(
        self,
        accounts_file: str,
        max_posts_per_profile: Optional[int] = None,
        max_retires_per_profile: Optional[int] = None,
    ) -> List[Dict]:
        """
        Scrapes reels for each account in parallel and returns results in a dictionary.

        :return: Dictionary mapping each username to a list of reel information dictionaries
        """
        account_manager: AccountManager = AccountManager(accounts_file)
        accounts: List[str] = account_manager.get_accounts()

        results: List[Dict] = list()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            future_to_username = dict()
            for username in accounts:
                future_to_username[
                    executor.submit(
                        self.scraper.get_user_reels,
                        username,
                        max_posts_per_profile,
                        max_retires_per_profile,
                    )
                ] = username

            for future in concurrent.futures.as_completed(future_to_username):
                username = future_to_username[future]
                try:
                    reels = future.result()
                    results += reels
                except Exception:
                    pass

        if self.data_saver is not None:
            if self.scraper.logger_manager is not None:
                self.scraper.logger_manager.log_saving_scraping_results(
                    self.data_saver.full_path
                )
            self.data_saver.save(results)
        if self.scraper.logger_manager is not None:
            self.scraper.logger_manager.log_finish_multiscraping(
                len(results), len(accounts)
            )

        return results
