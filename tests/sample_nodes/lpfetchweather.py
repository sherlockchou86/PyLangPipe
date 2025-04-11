import requests
import json
from pypinyin import lazy_pinyin
from langpipe import LPBaseInvoker

class LPFetchWeather(LPBaseInvoker):
    """
    weather search online using weatherapi service.
    """
    def __init__(self, name, 
                 api_key, 
                 api_url='http://api.weatherapi.com/v1/current.json', 
                 search_key='城市') -> None:
        super().__init__(name)
        self.__api_key = api_key
        self.__api_url = api_url
        self.__search_key = search_key
        self.__search_value = None
        self.__fetched_weather = None

    def _invoke(self, lpdata) -> None:
        extracted_params = lpdata.get('global_vars', {}).get('extracted_params', {})
        if self.__search_key in extracted_params and (search_value := extracted_params[self.__search_key]) is not None:
            self.__search_value = search_value
            self.__fetched_weather = self.__get_weather()
    
    def _after_handle(self, lpdata) -> None:
        super()._after_handle(lpdata)

        # update local variables
        record = lpdata['records'][-1]
        record['local_vars']['__api_key'] = self.__api_key
        record['local_vars']['__api_url'] = self.__api_url
        record['local_vars']['__search_key'] = self.__search_key
        record['local_vars']['search_value'] = self.__search_value

        # update global variables
        if self.__fetched_weather is not None:
            lpdata['final_out'] = json.dumps(self.__fetched_weather, indent=4, ensure_ascii=False)
            lpdata['global_vars']['fetched_weather'] = self.__fetched_weather
    
    def __get_weather(self) -> dict:
        # convert to pinyin
        search_value_py = ''.join(lazy_pinyin(self.__search_value))

        params = {
            "key": self.__api_key,
            "q": search_value_py,
            "aqi": "yes" 
        }
        response = requests.get(self.__api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            weather_data = {}

            weather_data['city'] = self.__search_value
            weather_data['update_time'] = data['current']['last_updated']
            weather_data['temperature'] = data['current']['temp_c']
            weather_data['condition'] = data['current']['condition']['text']
            weather_data['wind_kph'] = data['current']['wind_kph']
            weather_data['wind_dir'] = data['current']['wind_dir']
            weather_data['pressure_mb'] = data['current']['pressure_mb']
            weather_data['precip_mm'] = data['current']['precip_mm']
            weather_data['humidity'] = data['current']['humidity']
            weather_data['vis_km'] = data['current']['vis_km']
            weather_data['cloud'] = data['current']['cloud']
            weather_data['pm2_5'] = data['current']['air_quality']['pm2_5']

            return weather_data
        else:
            return None


