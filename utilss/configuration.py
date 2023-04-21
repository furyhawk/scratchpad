from pydantic import BaseSettings
from dotenv import dotenv_values
env = dotenv_values(".env")


def get_api_key():
    key = env["RIOT_API_KEY"]
    return key


def get_db_uri():
    key = env["ATLAS_URI"]
    return key


def get_db_name():
    key = env["DB_NAME"]
    return key


def get_latest_release():
    latest_release = env.get("LATEST_RELEASE", "12.12.450.4196")
    return latest_release


class Settings(BaseSettings):
    app_name: str = "tft champ"
    assets_dir: str = "assets"
    api_key: str = get_api_key()
    db_uri: str = get_db_uri()
    db_name: str = get_db_name()
    latest_release: str = get_latest_release()
    targetname: str = 'placement'
    max_count: int = 75
    # Regions (actually called platform) taken from https://developer.riotgames.com/docs/lol
    regions: dict = {
        "EUW1": {"code": "EUW1", "host": "euw1.api.riotgames.com"},
        "BR1": {"code": "BR1", "host": "br1.api.riotgames.com"},
        "EUN1": {"code": "EUN1", "host": "eun1.api.riotgames.com"},
        "JP1": {"code": "JP1", "host": "jp1.api.riotgames.com"},
        "KR": {"code": "KR", "host": "kr.api.riotgames.com"},
        "LA1": {"code": "LA1", "host": "la1.api.riotgames.com"},
        "LA2": {"code": "LA2", "host": "la2.api.riotgames.com"},
        "NA1": {"code": "NA1", "host": "na1.api.riotgames.com"},
        "OC1": {"code": "OC1", "host": "oc1.api.riotgames.com"},
        "TR1": {"code": "TR1", "host": "tr1.api.riotgames.com"},
        "RU": {"code": "RU", "host": "ru.api.riotgames.com"},
    }
    server: str = "na1"

    def get_api_host(self, region_code):
        if not region_code in self.regions:
            raise Exception("Region code not recognised")
        else:
            return self.regions[region_code]["host"]


settings = Settings()
