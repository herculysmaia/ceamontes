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
            hora_da_chuva = info['time_epoch']
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

            str_hora_inicio = dt.fromtimestamp(inicio_hora_da_chuva).strftime('%H')
            str_hora_maxima = dt.fromtimestamp(maximo_hora_da_chuva).strftime('%H')
            str_hora_fim = dt.fromtimestamp(fim_hora_da_chuva).strftime('%H')

            if agora > inicio_hora_da_chuva:
                if agora > maximo_hora_da_chuva:
                    if agora > fim_hora_da_chuva:
                        text = (
                            f'com a chuva prevista que começou às {str_hora_inicio}h, tendo a maior intensidade '
                            f'acontecido às {str_hora_maxima}h com {milimitros_acumulados} e o fim às {str_hora_fim}h')
                    else:
                        text = (
                            f'com a chuva prevista que começou às {str_hora_inicio}h, tendo a maior intensidade '
                            f'acontecido às {str_hora_maxima}h com {milimitros_acumulados} mm e fim previsto para às '
                            f'{str_hora_fim}h')
                else:
                    text = (f'com a chuva prevista que começou às {str_hora_inicio}h, tendo a maior intensidade às '
                            f'{str_hora_maxima}h com {milimitros_acumulados} mm e fim previsto para às {str_hora_fim}h')
            else:
                text = (f'com a chuva prevista para começar às {str_hora_inicio}h, tendo a maior intensidade às '
                        f'{str_hora_maxima}h com {milimitros_acumulados} mm e fim previsto para às {str_hora_fim}h')

    return text


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
    text = f'{round(data["forecast"]["forecastday"][1]["day"]["mintemp_c"])}'
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

if key is None:
    with open('key.txt', 'r') as arq:
        key = arq.read()

url = f'https://api.weatherapi.com/v1/forecast.json?key={key}&q={lat},{lon}&lang=pt&days=2&aqi=no&alerts=yes'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    data = abrir_dados()

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
