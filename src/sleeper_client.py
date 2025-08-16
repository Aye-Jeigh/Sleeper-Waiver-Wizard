import requests
import time
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
import diskcache as dc

class SleeperClient:
    BASE_URL = "https://api.sleeper.app/v1"
    CALLS_PER_MINUTE = 100
    
    def __init__(self, cache_dir: str = "./cache"):
        self.session = requests.Session()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = dc.Cache(str(self.cache_dir))
        
    @sleep_and_retry
    @limits(calls=CALLS_PER_MINUTE, period=60)
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _get_cached_or_fetch(self, endpoint: str, cache_key: str, cache_hours: int = 24) -> Optional[Any]:
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(hours=cache_hours):
                print(f"Using cached data for {cache_key}")
                return cached_data
        
        data = self._make_request(endpoint)
        if data is not None:
            self.cache[cache_key] = (data, datetime.now())
        return data
    
    def get_league(self, league_id: str) -> Optional[Dict]:
        endpoint = f"/league/{league_id}"
        return self._get_cached_or_fetch(endpoint, f"league_{league_id}", cache_hours=24)
    
    def get_rosters(self, league_id: str) -> Optional[List[Dict]]:
        endpoint = f"/league/{league_id}/rosters"
        return self._get_cached_or_fetch(endpoint, f"rosters_{league_id}", cache_hours=1)
    
    def get_users(self, league_id: str) -> Optional[List[Dict]]:
        endpoint = f"/league/{league_id}/users"
        return self._get_cached_or_fetch(endpoint, f"users_{league_id}", cache_hours=24)
    
    def get_all_players(self) -> Optional[Dict]:
        endpoint = "/players/nfl"
        return self._get_cached_or_fetch(endpoint, "all_players", cache_hours=168)
    
    def get_trending_players(self, sport: str = "nfl", type: str = "add", hours: int = 24, limit: int = 25) -> Optional[List[Dict]]:
        endpoint = f"/players/{sport}/trending/{type}?lookback_hours={hours}&limit={limit}"
        cache_key = f"trending_{sport}_{type}_{hours}_{limit}"
        return self._get_cached_or_fetch(endpoint, cache_key, cache_hours=1)
    
    def get_stats(self, season: int, week: int, season_type: str = "regular") -> Optional[Dict]:
        endpoint = f"/stats/nfl/{season_type}/{season}/{week}"
        cache_key = f"stats_{season}_{season_type}_{week}"
        return self._get_cached_or_fetch(endpoint, cache_key, cache_hours=6)
    
    def get_projections(self, season: int, week: int, season_type: str = "regular") -> Optional[Dict]:
        endpoint = f"/projections/nfl/{season_type}/{season}/{week}"
        cache_key = f"projections_{season}_{season_type}_{week}"
        return self._get_cached_or_fetch(endpoint, cache_key, cache_hours=6)
    
    def get_matchups(self, league_id: str, week: int) -> Optional[List[Dict]]:
        endpoint = f"/league/{league_id}/matchups/{week}"
        cache_key = f"matchups_{league_id}_{week}"
        return self._get_cached_or_fetch(endpoint, cache_key, cache_hours=1)
    
    def get_transactions(self, league_id: str, week: int) -> Optional[List[Dict]]:
        endpoint = f"/league/{league_id}/transactions/{week}"
        cache_key = f"transactions_{league_id}_{week}"
        return self._get_cached_or_fetch(endpoint, cache_key, cache_hours=1)
    
    def clear_cache(self):
        self.cache.clear()
        print("Cache cleared")