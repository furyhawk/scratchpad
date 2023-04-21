from dataclasses import dataclass

from omegaconf import MISSING

from hydra.core.config_store import ConfigStore


@dataclass
class WebConfig:
    user_agent: str = MISSING
    parser: str = "lxml"
    companies_url: str = MISSING
    ticker_url: str = MISSING
    output_filename: str = MISSING


@dataclass
class CompaniesMarketCapConfig(WebConfig):
    max_companies: int = MISSING
    start_from: int = MISSING


def register_configs() -> None:
    cs: ConfigStore = ConfigStore.instance()
    cs.store(
        group="webscraping_lib/web",
        name="companiesmarketcap",
        node=CompaniesMarketCapConfig,
    )
