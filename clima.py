from datetime import datetime as dt, timedelta

import requests
import json
import os


def abrir_dados():
    resposta_padrao = {
        "list": [{
            "dt": 0,
            "main": {
                "temp": 0,
                "temp_min": 0,
                "temp_max": 0,
                "humidity": 0,
            },
            "rain": {
                "1h": 0,
            },
            "weather": [{
                "description": "INDETERMINADO",
                "icon": "01n"
            }],
            "clouds": {
                "all": 0
            },
            "sys": {
                "pod": "n"},
            "city": {
                "sunrise": 0,
                "sunset": 0
            }
        }]
    }

    try:
        with open('dados.json', 'r') as ops:
            config = json.load(ops)
    except (ValueError, FileNotFoundError):
        with open('dados.json', 'w') as ops:
            json.dump(resposta_padrao, ops)
        return resposta_padrao

    return config


def obter_chance_de_chuva():
    agora = (dt.now() + timedelta(minutes=15)).timestamp()
    milimitros_acumulados = 0
    inicio_hora_da_chuva = 2000000000
    maximo_hora_da_chuva = 0
    fim_hora_da_chuva = 0

    lista_dado = data['forecast']['forecastday'][0]['hour']
    text = 'sem previsão de chuva'
    for info in lista_dado:
        if info['precip_mm'] != 0:
            hora_da_chuva = info['date_epoch']
            milimetros = info['precip_mm']

            if hora_da_chuva < inicio_hora_da_chuva:
                inicio_hora_da_chuva = hora_da_chuva
                maximo_hora_da_chuva = hora_da_chuva
                fim_hora_da_chuva = hora_da_chuva
                milimitros_acumulados = milimetros

            if milimitros_acumulados < milimetros:
                maximo_hora_da_chuva = hora_da_chuva
                fim_hora_da_chuva = hora_da_chuva
                milimitros_acumulados = milimetros

            if hora_da_chuva > fim_hora_da_chuva:
                fim_hora_da_chuva = hora_da_chuva

            str_hora_inicio = dt.fromtimestamp(inicio_hora_da_chuva).strftime('%H:%M')
            str_hora_maxima = dt.fromtimestamp(maximo_hora_da_chuva).strftime('%H:%M')
            str_hora_fim = dt.fromtimestamp(fim_hora_da_chuva).strftime('%H:%M')

            if inicio_hora_da_chuva < agora < maximo_hora_da_chuva:
                text = (f'com a chuva prevista que começou às {str_hora_inicio}, tendo a maior intensidade às '
                        f'{str_hora_maxima} com {milimitros_acumulados} mm e fim previsto para às {str_hora_fim}')

            elif agora < fim_hora_da_chuva:
                text = (f'com a chuva prevista que começou às {str_hora_inicio}, tendo a maior intensidade acontecido '
                        f'às {str_hora_maxima} com {milimitros_acumulados} mm e fim previsto para às {str_hora_fim}')

            elif agora >= fim_hora_da_chuva:
                text = (f'com a chuva prevista que começou às {str_hora_inicio}, tendo a maior intensidade acontecido '
                        f'às {str_hora_maxima} com {milimitros_acumulados} e o fim às {str_hora_fim}')
            else:
                text = (f'com a chuva prevista para começar às {str_hora_inicio}, tendo a maior intensidade às '
                        f'{str_hora_maxima} com {milimitros_acumulados} mm e fim previsto para às {str_hora_fim}')

    return text


def calcular_duracao_noite():
    hora_nascer_sol_unix = data['forecast']['forecastday'][1]['astro']['sunrise']
    hora_por_sol_unix = data['forecast']['forecastday'][0]['astro']['sunset']

    hora_nascer_lua_unix = data['forecast']['forecastday'][0]['astro']['moonrise']
    hora_por_lua_unix = data['forecast']['forecastday'][0]['astro']['moonset']

    if hora_nascer_lua_unix == 'No moonrise':
        nascer_da_lua = dt.strptime(hora_nascer_sol_unix, "%I:%M %p").replace(hour=0, minute=0, second=0)
    else:
        nascer_da_lua = dt.strptime(hora_nascer_lua_unix, "%I:%M %p")

    if hora_por_lua_unix == 'No moonset':
        por_da_lua = dt.strptime(hora_nascer_sol_unix, "%I:%M %p").replace(hour=0, minute=0, second=0)
    else:
        por_da_lua = dt.strptime(hora_por_lua_unix, "%I:%M %p")

    nascer_do_sol = dt.strptime(hora_nascer_sol_unix, "%I:%M %p")
    por_do_sol = dt.strptime(hora_por_sol_unix, "%I:%M %p")

    duracao_noite = nascer_do_sol - por_do_sol

    horas_noite = int(duracao_noite.seconds / 3600)
    minutos_noite = int((duracao_noite.seconds - horas_noite * 3600) / 60)

    nasce_lua = f'{nascer_da_lua.hour:02d}:{nascer_da_lua.minute:02d}'
    por_lua = f'{por_da_lua.hour:02d}:{por_da_lua.minute:02d}'

    fase = fase_em_pt[data['forecast']['forecastday'][0]['astro']['moon_phase']]
    emoji_texto = fase_em_emojis[data['forecast']['forecastday'][0]['astro']['moon_phase']]
    iluminada = data['forecast']['forecastday'][0]['astro']['moon_illumination']

    resposta = (f'{horas_noite} horas e {minutos_noite} minutos, com a Lua na fase {fase} {emoji_texto} ({iluminada}% '
                f'iluminada), surgindo às {nasce_lua} e recolhendo-se às {por_lua}')

    return resposta


def calcular_duracao_dia():
    hora_nascer_sol_unix = data['forecast']['forecastday'][0]['astro']['sunrise']
    hora_por_sol_unix = data['forecast']['forecastday'][0]['astro']['sunset']

    nascer_do_sol = dt.strptime(hora_nascer_sol_unix, "%I:%M %p")
    por_do_sol = dt.strptime(hora_por_sol_unix, "%I:%M %p")

    duracao_noite = por_do_sol - nascer_do_sol

    horas_noite = int(duracao_noite.seconds / 3600)
    minutos_noite = int((duracao_noite.seconds - horas_noite * 3600) / 60)

    resposta = f'{horas_noite} horas e {minutos_noite} minutos'

    return resposta


def condicao_noite():
    hora_da_previsao = 20

    descricao = data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['condition']['text']
    figura = emoji[data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['condition']['code']]
    cobertura = data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['cloud']
    temperatura = round(data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['temp_c'])
    chance_de_chuva = data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['chance_of_rain']
    milimetros_de_chuva = data['forecast']['forecastday'][0]['hour'][hora_da_previsao]['precip_mm']

    if chance_de_chuva == 0:
        chuva = 'sem chance de chuva'
    else:
        if milimetros_de_chuva == 0:
            chuva = f'{chance_de_chuva}% de chance de chuva'
        else:
            chuva = f'{chance_de_chuva}% de chance de chover {milimetros_de_chuva} mm'

    text = f'{descricao} {figura}, com {cobertura}% do céu coberto e temperatura de {temperatura}°C, {chuva}'
    return text


def condicao_atual() -> str:
    descricao = data['current']['condition']['text']
    figura = emoji[data['current']['condition']['code']]
    text = f'{descricao} {figura}'
    return text


def temperatura_minima():
    text = f'{round(data["forecast"]["forecastday"][0]["day"]["mintemp_c"])}'
    return text


def temperatura_maxima():
    text = f'{round(data["forecast"]["forecastday"][0]["day"]["maxtemp_c"])}'
    return text


def temperatura_atual():
    text = f'{round(data["current"]["temp_c"])}'
    return text


def umidade_atual():
    text = f'{data["current"]["humidity"]}'
    return text


def visibilidade_atual():
    text = f'{data["current"]["cloud"]}'
    return text


lat = -16.715767
lon = -43.863275

key = os.getenv("API_KEY")

url = f'https://api.weatherapi.com/v1/forecast.json?key={key}&q={lat},{lon}&lang=pt&days=2&aqi=no&alerts=yes'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    data = abrir_dados()

fase_em_pt = {
    "New Moon": "nova",
    "Waxing Crescent": "crescente côncavo",
    "First Quarter": "primeiro quarto",
    "Waxing Gibbous": "crescente convexo",
    "Full Moon": "cheia",
    "Waning Gibbous": "minguante convexo",
    "Last Quarter": "último quarto",
    "Waning Crescent": "minguante côncavo"
}

fase_em_emojis = {
    "New Moon": "🌑",
    "Waxing Crescent": "🌘",
    "First Quarter": "🌗",
    "Waxing Gibbous": "🌖",
    "Full Moon": "🌕",
    "Waning Gibbous": "🌔",
    "Last Quarter": "🌓",
    "Waning Crescent": "🌒"
}

emoji = {
    1000: "☀️",
    1003: "⛅",
    1006: "☁️",
    1009: "☁️",
    1030: "🌫️",
    1063: "🌦️",
    1066: "🌨️",
    1069: "🌨️❄️",
    1072: "🌧️❄️",
    1087: "⛈️",
    1114: "🌬️🌨️",
    1117: "❄️🌬️",
    1135: "🌁",
    1147: "🌁❄️",
    1150: "🌦️🌧️",
    1153: "🌧️",
    1168: "🌧️❄️",
    1171: "🌧️❄️",
    1180: "🌦️🌧️",
    1183: "🌧️",
    1186: "🌧️",
    1189: "🌧️",
    1192: "🌧️☔",
    1195: "🌧️☔",
    1198: "🌧️❄️",
    1201: "🌧️❄️",
    1204: "🌨️❄️",
    1207: "🌨️❄️",
    1210: "🌨️",
    1213: "🌨️❄️",
    1216: "🌨️❄️",
    1219: "🌨️❄️",
    1222: "🌨️❄️",
    1225: "🌨️❄️",
    1237: "🌧️❄️",
    1240: "🌧️☔",
    1243: "🌧️☔",
    1246: "🌧️☔",
    1249: "🌨️❄️",
    1252: "🌨️❄️",
    1255: "🌨️❄️",
    1258: "🌨️❄️",
    1261: "🌧️❄️",
    1264: "🌧️❄️",
    1273: "🌩️🌧️",
    1276: "🌩️🌧️",
    1282: "🌩️🌨️❄️"
}