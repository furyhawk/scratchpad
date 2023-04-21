from typing import Any, Literal
import logging
from math import ceil
import datetime

from dataclasses import dataclass

import requests
from requests import Response
from bs4 import BeautifulSoup
import pandas as pd

from tqdm import tqdm

import webscraping_lib

from omegaconf import MISSING, OmegaConf, DictConfig
import hydra

from hydra.core.config_store import ConfigStore

# from utils import general_utils

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Config:
    web: webscraping_lib.CompaniesMarketCapConfig = MISSING
    debug: bool = False


cs: ConfigStore = ConfigStore.instance()
cs.store(name="base_config", node=Config)

# webscraping_lib registers its configs
# in webscraping_lib/web
webscraping_lib.register_configs()


def float_or_na(value: Any) -> float | Literal[0]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


def get_url_page(url_link, user_agent, parser) -> BeautifulSoup | Literal[""]:
    """This accepts an URL as a parameter,
    accesses and loads the webpage into a variable
    retuns a document of the type BeautifulSoup"""

    # uses requests function to access and load the web page
    stock_page_response: Response = requests.get(
        url_link, headers={"user-agent": user_agent}
    )

    if not stock_page_response.ok:
        logger.info(f"Status code for {url_link}: {stock_page_response.status_code}")
        # raise Exception('Failed to fetch web page ' + url_link)
        return ""

    # If the status code is success , the page is sent through html parser and builds a parsed document.
    stock_page_doc: BeautifulSoup = BeautifulSoup(stock_page_response.text, parser)

    # Returns a beautifulSoup document.
    return stock_page_doc


def get_stocks(num_stocks: int, start_num: int, cfg: DictConfig):
    """
    This functions builds a list of most popular stock symbols.
    Returns the list of N number of popular stocks
    """
    # Get the number of pages to access based on the number of stocks that need to be processed. each page has 100 stocks
    start_page: int = int((lambda x: 1 if x < 1 else ceil(x / 100))(start_num))
    end_page: int = int(
        (lambda x: 1 if x < 1 else ceil(x / 100))(start_num + num_stocks)
    )

    stocks_symbols = []
    for page_number in range(start_page, end_page + 1):
        stocks_url = cfg.web.companies_url + str(page_number) + "/"

        logger.info(f"Web Page: {stocks_url}")
        # Call the function 'get_url_page' and get parsed html document
        stocks_symbols_tags = get_url_page(
            url_link=stocks_url,
            user_agent=cfg.web.user_agent,
            parser=cfg.web.parser,
        ).find_all("div", {"class": "company-code"})

        # Extract ticker symbol name from the tag 'div' in the document
        for stocks_symbols_tag in stocks_symbols_tags:
            stocks_symbols.append(stocks_symbols_tag.text.strip())

    # Return the list with N stocks
    return stocks_symbols[:num_stocks]


def get_name_n_symbol(companyName: str) -> tuple[str, str]:
    """
    A Helper function to accept Name and returns company Name and ticker symbol
    """
    cName: list[str] = companyName.split("(")
    name: str = "(".join(cName[:-1]).strip()
    ticker: str = cName[-1].strip(")")
    return (name, ticker)


def get_ticker_details(ticker_symbol: str, cfg: DictConfig):
    """
    This function accepts the ticker symbol,
    gets the html parsed document, finds appropriate tags and its value(text)
    massages the data and returns stocks details as a python Dictionary
    """
    # time.sleep(random.uniform(0, 1))
    # logger.info("Processing : ", ticker_symbol)
    ticker_url: str = "https://finance.yahoo.com/quote/" + ticker_symbol

    # get html parsed document.
    stock_page_doc: BeautifulSoup | Literal[""] = get_url_page(
        url_link=ticker_url,
        user_agent=cfg.web.user_agent,
        parser=cfg.web.parser,
    )

    if len(stock_page_doc) == 0:
        return ""

    # Use find function of BeatufulSoup objet to get the values of the tags
    # Use helper function get_name_n_symbol to extract company name and ticker symbol from the h1 name
    company_text = stock_page_doc.find("h1")
    if company_text is None:
        return ""
    cName, ticker = get_name_n_symbol(company_text.text)
    MarketPrice = stock_page_doc.find(
        "fin-streamer",
        {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)", "data-field": "regularMarketPrice"},
    ).text.replace(",", "")
    previousClosePrice = stock_page_doc.find(
        "td", {"class": "Ta(end) Fw(600) Lh(14px)", "data-test": "PREV_CLOSE-value"}
    ).text.replace(",", "")
    Volume = stock_page_doc.find(
        "td", {"class": "Ta(end) Fw(600) Lh(14px)", "data-test": "TD_VOLUME-value"}
    ).text.replace(",", "")
    pe_ratio = stock_page_doc.find(
        "td", {"class": "Ta(end) Fw(600) Lh(14px)", "data-test": "PE_RATIO-value"}
    ).text.replace(",", "")
    eps_ratio = stock_page_doc.find(
        "td", {"class": "Ta(end) Fw(600) Lh(14px)", "data-test": "EPS_RATIO-value"}
    ).text.replace(",", "")

    # Some of the stocks(ex.S&P) does not have market capital, using lambda function to replace such vaules with 0
    MarketCap = (lambda x: x.text.replace(",", "") if x != None else "0")(
        stock_page_doc.find(
            "td", {"class": "Ta(end) Fw(600) Lh(14px)", "data-test": "MARKET_CAP-value"}
        )
    )

    ticker_dict = {
        "Company": cName.replace(",", ""),
        "Symbol": ticker,
        "Marketprice": float_or_na(MarketPrice),
        "previousClosePrice": float_or_na(previousClosePrice),
        "changeInPrice": round(
            float_or_na(MarketPrice) - float_or_na(previousClosePrice), 2
        ),
        "pe_ratio": float_or_na(pe_ratio),
        "eps_ratio": float_or_na(eps_ratio),
        "Volume": int(Volume),
        "MarketCap": MarketCap,
    }

    # Return Dictionary with stock details
    return ticker_dict


def write_csv(dict_items, file_name: str) -> None:
    """
    Accepts list of python dictionary with stock details and write it to a csv file
    logger.infos success message upon completing the writing to the file
    """

    # open the file for writing
    with open(file_name, "w") as f:

        # Get headers(keys) of the first dictionary from the list. Convert to a list, join each element of the list
        # with ',' to form a string and write to the file.
        headers = list(dict_items[0].keys())
        f.write(",".join(headers) + "\n")

        # For each Dictionary item, create a list with values and write it to the file
        for dict_item in dict_items:
            values = []
            for header in headers:
                try:
                    values.append(str(dict_item.get(header, "")))
                except:
                    pass
            f.write(",".join(values) + "\n")

    logger.info(f"Writing to file '{file_name}' completed")


def verify_results(file_name: str) -> None:
    """
    This Function verifies the File Output.
    Accepts file name as the parameter and displays sample output and row count.
    """

    # Create the dataFrame with the csv file
    stocks_df: pd.DataFrame = pd.read_csv(file_name)

    # logger.info a record count of a single column
    logger.info("")
    logger.info("Checking Output written to the file")
    logger.info("---------------------------------------")
    logger.info(f"Number of records written to the file : {stocks_df.count()[1]}")
    logger.info("")
    # logger.info a sample output of first 4 rows in the file alson with its headers
    logger.info("Sample Output : ")
    logger.info(stocks_df.head(4))


def scrape_stocks_info(num_stocks: int, start_num: int, cfg: DictConfig) -> None:
    """
    This function Accepts number of stocks to be processed and writes the stock information to a file
    """

    # Gets List of popular stocks and passes them to the function 'get_ticker_details' one by one.
    # This is return a list of dictionaries with stock details.
    logger.info("Start processing Stock symbols...")
    stocks_info = []
    pbar = tqdm(get_stocks(num_stocks=num_stocks, start_num=start_num, cfg=cfg))
    for ticker_name in pbar:
        pbar.set_description(f"Processing {ticker_name}")
        stocks_info.append(get_ticker_details(ticker_name, cfg))

    logger.info("End processing Stock symbols...")

    # Pass the list of dictionies to the 'write_csv' function which writes it to the file.
    today: datetime = datetime.datetime.now()
    file_name: str = (
        str(start_num)
        + "_to_"
        + str(start_num + num_stocks - 1)
        + cfg.web.output_filename
        + today.strftime("%Y-%m-%d")
        + ".csv"
    )
    write_csv(stocks_info, file_name)

    # Verify Results:
    verify_results(file_name)


@hydra.main(
    version_base=None,
    config_path="conf",
    config_name="config",
)
def app(cfg: DictConfig) -> None:
    logger.info(OmegaConf.to_yaml(cfg))
    scrape_stocks_info(
        num_stocks=cfg.web.max_companies, start_num=cfg.web.start_from, cfg=cfg
    )


if __name__ == "__main__":
    app()
