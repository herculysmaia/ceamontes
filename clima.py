from datetime import datetime as dt, timedelta

import requests
import json


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
    agora = (dt.now() + timedelta(minutes=15))
    milimitros_acumulados = 0
    inicio_hora_da_chuva = agora + timedelta(days=7)
    maximo_hora_da_chuva = 0
    fim_hora_da_chuva = 0

    hora = data['hourly']['time'][24:49]
    chuva = data['hourly']['rain'][24:49]
    text = 'sem previsão de chuva'

    for item_hora, item_chuva in zip(hora, chuva):
        if item_chuva != 0:
            hora_da_chuva = dt.strptime(item_hora, "%Y-%m-%dT%H:%M")
            milimetros = item_chuva

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

            str_hora_inicio = inicio_hora_da_chuva.strftime('%H')
            str_hora_maxima = maximo_hora_da_chuva.strftime('%H')
            str_hora_fim = fim_hora_da_chuva.strftime('%H')

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
    hora_da_previsao = 44

    descricao = dict_descricao[data['hourly']['weathercode'][hora_da_previsao]]
    cobertura = data['hourly']['cloudcover'][hora_da_previsao]
    temperatura = int(data['hourly']['temperature_80m'][hora_da_previsao])
    chance_de_chuva = data['hourly']['precipitation_probability'][hora_da_previsao]
    milimetros_de_chuva = data['hourly']['rain'][hora_da_previsao]

    if chance_de_chuva == 0:
        chuva = 'sem chance de chuva'
    else:
        if milimetros_de_chuva == 0:
            chuva = f'{chance_de_chuva}% de chance de chuva'
        else:
            chuva = f'{chance_de_chuva}% de chance de chover {milimetros_de_chuva} mm'

    text = f'{descricao}, com {cobertura}% do céu coberto e temperatura de {temperatura}°C, {chuva}'
    return text


def condicao_atual() -> str:
    descricao = dict_descricao[data['current_weather']['weathercode']]
    return descricao


def temperatura_minima():
    temperatura = int(data['daily']['temperature_2m_min'][2])
    return temperatura


def temperatura_maxima():
    temperatura = int(data['daily']['temperature_2m_max'][1])
    return temperatura


def temperatura_atual():
    temperatura = int(data['current_weather']['temperature'])
    return temperatura


def umidade_atual():
    umidade = data['hourly']['relativehumidity_2m'][42]
    return umidade


def visibilidade_atual():
    cobertura = data['hourly']['cloudcover'][42]
    return cobertura


def obter_condicoes_eclipse():

    url_14_10 = ('https://api.open-meteo.com/v1/forecast?latitude=-16.715768&longitude=-43.863273&'
                 'hourly=temperature_2m,precipitation_probability,rain,weathercode,cloudcover,cloudcover_low,'
                 'cloudcover_mid,cloudcover_high,visibility,uv_index&timezone=America%2FSao_Paulo&'
                 'start_date=2023-10-14&end_date=2023-10-14')

    reposta_previsao = requests.get(url_14_10)

    texto = '(dados indiponíves no momento)'

    if reposta_previsao.status_code == 200:
        previsao = reposta_previsao.json()

        hora_eclipse = '2023-10-14T16:00'

        indice_hora = previsao['hourly']['time'].index(hora_eclipse)

        condicao = dict_descricao[previsao['hourly']['weathercode'][indice_hora]]
        temperatura = previsao['hourly']['temperature_2m'][indice_hora]
        cobertura = previsao['hourly']['cloudcover'][indice_hora]
        chuva = previsao['hourly']['rain'][indice_hora+1]

        texto_cobertura = f"com {cobertura}% do céu coberto"

        if cobertura == 0:
            texto_cobertura = 'sem nuvens'

        precicipitacao = previsao['hourly']['precipitation_probability'][indice_hora]

        texto_chuva = 'sem chance de chuva'

        if precicipitacao is not None and precicipitacao > 0:
            texto_chuva = f'com {precicipitacao}% de chance de chover {chuva} mm no horário'

        texto = f'{condicao}, fazendo {temperatura:.0f}°C, {texto_cobertura} e {texto_chuva}'

    return texto


lat = -16.715767
lon = -43.863275


url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,"
       f"relativehumidity_2m,precipitation_probability,rain,weathercode,cloudcover,temperature_80m&daily=weathercode,"
       f"temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_hours,"
       f"precipitation_probability_max&current_weather=true&timezone=America%2FSao_Paulo&past_days=1&forecast_days=3")

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    data = abrir_dados()

dict_descricao = {
    0: "☀️ céu limpo",
    1: "🌤 principalmente claro",
    2: "⛅️ parcialmente nublado",
    3: "☁️ nublado",
    45: "🌫️ neblina",
    48: "🌁 névoa",
    51: "💦 garoa leve",
    53: "☔ garoa moderada",
    55: "🌦️ garoa densa",
    56: "🌦️ garoa congelante leve",
    57: "🌧️ garoa congelante densa",
    61: "🌦️ chuva leve",
    63: "🌧️ chuva moderada",
    65: "⛈️ chuva forte",
    66: "🌧️ chuva congelante leve",
    67: "🌨️ chuva congelante intensa",
    71: "🌨️ queda de neve leve",
    73: "🌨️ queda de neve moderada",
    75:	"🌨️ queda de neve intensa",
    77: "❄️ Nevasca",
    80: "☔ pancadas de chuva leve",
    81: "🌦️ pancadas de chuva moderada",
    82: "🌧️ pancadas de chuva violentas",
    85: "🌨️ neve leve",
    86: "❄️ neve pesada",
    95: "🌩️ trovoada ligeira",
    96: "⛈️ trovoada com granizo leve",
    99: "⛈️ trovoada com granizo intensa",
}
