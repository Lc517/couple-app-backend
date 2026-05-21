import os
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/weather", tags=["weather"])

QWEATHER_KEY = os.getenv("QWEATHER_KEY", "")
QWEATHER_BASE = "https://devapi.qweather.com/v7"


def generate_tips(weather_data: dict, forecast: dict) -> str:
    tips = []
    precip = float(forecast.get("precip", 0) or 0)
    temp_max = int(forecast.get("tempMax", 25) or 25)
    temp_min = int(forecast.get("tempMin", 15) or 15)
    wind_scale = int(forecast.get("windScaleDay", 0) or 0)
    icon = forecast.get("icon", "")

    if precip > 0:
        tips.append("记得带伞")
    if temp_max - temp_min > 10:
        tips.append("温差较大，注意添减衣物")
    elif temp_max < 10:
        tips.append("天气较冷，多穿点")
    elif temp_max > 30:
        tips.append("天气炎热，注意防暑")
    if wind_scale >= 4:
        tips.append("风较大，注意保暖")

    # 根据天气图标判断
    if icon in ("1001", "1002"):
        pass  # 晴/多云，不用特别提醒
    elif icon in ("1003", "1004"):
        tips.append("天阴，可能要下雨")
    elif icon in ("1053", "1054", "1055"):
        tips.append("有雾，注意安全")

    return "，".join(tips) if tips else "天气不错~"


@router.get("")
async def get_weather(lat: float = 29.03, lon: float = 111.69):
    """获取天气信息，传入经纬度，默认常德"""
    if not QWEATHER_KEY:
        return {"error": "未配置天气API密钥", "tips": "请配置 QWEATHER_KEY"}

    location = f"{lon},{lat}"

    async with httpx.AsyncClient() as client:
        # 获取实时天气
        current_resp = await client.get(
            f"{QWEATHER_BASE}/weather/now",
            params={"location": location, "key": QWEATHER_KEY},
        )
        # 获取3天预报
        forecast_resp = await client.get(
            f"{QWEATHER_BASE}/weather/3d",
            params={"location": location, "key": QWEATHER_KEY},
        )

    current = current_resp.json().get("now", {})
    forecasts = forecast_resp.json().get("daily", [])
    tomorrow = forecasts[1] if len(forecasts) > 1 else forecasts[0] if forecasts else {}

    tips = generate_tips(current, tomorrow)

    return {
        "current": {
            "temp": current.get("temp"),
            "text": current.get("text"),
            "icon": current.get("icon"),
            "humidity": current.get("humidity"),
            "wind_scale": current.get("windScale"),
        },
        "tomorrow": {
            "temp_max": tomorrow.get("tempMax"),
            "temp_min": tomorrow.get("tempMin"),
            "text_day": tomorrow.get("textDay"),
            "text_night": tomorrow.get("textNight"),
            "icon_day": tomorrow.get("iconDay"),
            "precip": tomorrow.get("precip"),
            "wind_scale": tomorrow.get("windScaleDay"),
        },
        "tips": tips,
    }
