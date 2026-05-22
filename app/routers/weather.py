import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/weather", tags=["weather"])

WMO_CODES = {
    0: "晴", 1: "大部晴", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "小毛毛雨", 53: "毛毛雨", 55: "大毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    66: "冻雨", 67: "冻雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    77: "雪粒", 80: "小阵雨", 81: "阵雨", 82: "大阵雨",
    85: "小阵雪", 86: "大阵雪",
    95: "雷暴", 96: "雷暴伴冰雹", 99: "雷暴伴大冰雹",
}


def generate_tips(temp_max: float, temp_min: float, precip: float, wind: float, weather_code: int) -> str:
    tips = []
    if precip > 0:
        tips.append("记得带伞")
    if temp_max - temp_min > 10:
        tips.append("温差较大，注意添减衣物")
    elif temp_max < 10:
        tips.append("天气较冷，多穿点")
    elif temp_max > 30:
        tips.append("天气炎热，注意防暑")
    if wind >= 4:
        tips.append("风较大，注意保暖")
    return "，".join(tips) if tips else "天气不错~"


@router.get("")
async def get_weather(lat: float = 29.03, lon: float = 111.69):
    """获取天气信息，使用 Open-Meteo 免费 API"""
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "Asia/Shanghai",
            "forecast_days": 2,
        })
        data = resp.json()

    current = data.get("current", {})
    daily = data.get("daily", {})

    current_code = current.get("weather_code", 0)
    tomorrow_code = daily.get("weather_code", [0, 0])
    tomorrow_code = tomorrow_code[1] if len(tomorrow_code) > 1 else tomorrow_code[0]

    temp_max_list = daily.get("temperature_2m_max", [25, 25])
    temp_min_list = daily.get("temperature_2m_min", [15, 15])
    precip_list = daily.get("precipitation_sum", [0, 0])
    wind_list = daily.get("wind_speed_10m_max", [0, 0])

    t_max = temp_max_list[1] if len(temp_max_list) > 1 else temp_max_list[0]
    t_min = temp_min_list[1] if len(temp_min_list) > 1 else temp_min_list[0]
    precip = precip_list[1] if len(precip_list) > 1 else precip_list[0]
    wind = wind_list[1] if len(wind_list) > 1 else wind_list[0]

    tips = generate_tips(t_max, t_min, precip, wind, tomorrow_code)

    wind_scale = round(wind / 3.6)  # km/h to Beaufort scale (rough)

    return {
        "current": {
            "temp": str(round(current.get("temperature_2m", 0))),
            "text": WMO_CODES.get(current_code, "未知"),
            "icon": str(current_code),
            "humidity": str(round(current.get("relative_humidity_2m", 0))),
            "wind_scale": str(wind_scale),
        },
        "tomorrow": {
            "temp_max": str(round(t_max)),
            "temp_min": str(round(t_min)),
            "text_day": WMO_CODES.get(tomorrow_code, "未知"),
            "text_night": WMO_CODES.get(tomorrow_code, "未知"),
            "icon_day": str(tomorrow_code),
            "precip": str(round(precip, 1)),
            "wind_scale": str(wind_scale),
        },
        "tips": tips,
    }
