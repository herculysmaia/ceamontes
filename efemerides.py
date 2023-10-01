from skyfield import api, almanac
from datetime import datetime as dt, timedelta

from skyfield.framelib import ecliptic_frame
from skyfield.magnitudelib import planetary_magnitude
from skyfield.starlib import Star

TS = api.load.timescale()
EPH = api.load('de421.bsp')

HOJE = dt.now(tz=api.utc) + timedelta(minutes=15)

MONTES_CLAROS = api.Topos(latitude_degrees=-16.715767, longitude_degrees=-43.863275)


def _calcular_ponto(t0, t1, f):
    t, y = almanac.find_discrete(t0, t1, f)

    return t, y


def _calcular_fase_da_lua(t):
    terra = EPH['earth'].at(t)
    sol = terra.observe(EPH['sun']).apparent()
    lua = terra.observe(EPH['moon']).apparent()

    _, sol_lon, _ = sol.frame_latlon(ecliptic_frame)
    _, lua_lon, _ = lua.frame_latlon(ecliptic_frame)

    fase = (lua_lon.degrees - sol_lon.degrees) % 360.0
    iluminada = 100.0 * lua.fraction_illuminated(EPH['sun'])

    if fase < 90:
        texto_fase = 'crescente côncavo 🌒'
    elif fase == 90:
        texto_fase = 'primeiro quarto 🌓'
    elif 90 < fase < 180:
        texto_fase = 'crescente convexo 🌔'
    elif fase == 180:
        texto_fase = 'cheia 🌕'
    elif 180 < fase < 270:
        texto_fase = 'minguante convexo 🌖'
    elif fase == 270:
        texto_fase = 'último quarto 🌗'
    elif 270 < fase < 360:
        texto_fase = 'minguante côncavo 🌘'
    else:
        texto_fase = '🌑'

    return texto_fase, int(iluminada)

class Calendario:
    dicionario_mes = {
        1: 'janeiro',
        2: 'fevereiro',
        3: 'março',
        4: 'abril',
        5: 'maio',
        6: 'junho',
        7: 'julho',
        8: 'agosto',
        9: 'setembro',
        10: 'outubro',
        11: 'novembro',
        12: 'dezembro'
    }

    @staticmethod
    def dia_ano():
        inicio_do_ano = dt(HOJE.year, 1, 1, tzinfo=api.utc)
        diferenca = HOJE - inicio_do_ano
        return diferenca.days

    @staticmethod
    def dias_no_ano():
        inicio_do_ano = dt(HOJE.year, 1, 1, tzinfo=api.utc)
        fim_do_ano = dt(HOJE.year + 1, 1, 1, tzinfo=api.utc)
        diferenca = fim_do_ano - inicio_do_ano
        return diferenca.days

    @staticmethod
    def dias_final_de_ano():
        fim_do_ano = dt(HOJE.year, 12, 31, tzinfo=api.utc)
        diferenca = fim_do_ano - HOJE
        return diferenca.days

    @staticmethod
    def comemorativa():
        return ''

    def dia_de_hoje(self):
        dia = HOJE.day
        mes = self.dicionario_mes[HOJE.month]
        ano = HOJE.year

        text = f'{dia} de {mes} de {ano}'
        return text


class Evento(Calendario):

    planetas = [{'nome': 'Mercúrio', 'dados': EPH['mercury barycenter']},
                {'nome': 'Vênus', 'dados': EPH['venus barycenter']},
                {'nome': 'Marte', 'dados': EPH['mars barycenter']},
                {'nome': 'Júpiter', 'dados': EPH['jupiter barycenter']},
                {'nome': 'Saturno', 'dados': EPH['saturn barycenter']}]

    def __init__(self):
        super().__init__()

    @staticmethod
    def _obter_horario_de_sirius():
        sirius = Star(ra_hours=(6, 45, 8.9173), dec_degrees=(-16, 42, 58))

        amanha = HOJE + timedelta(days=1)

        f = almanac.meridian_transits(EPH, sirius, MONTES_CLAROS)

        t, e = _calcular_ponto(TS.utc(HOJE), TS.utc(amanha), f)

        horario = (t[e == 1][0] - timedelta(hours=3)).utc_datetime()

        text = (f'A próxima passagem da estrela Sírius pelo zênite será às '
                f'{horario.hour:02d}:{horario.minute:02d}')

        return text

    @staticmethod
    def _obter_nascer_e_por(t0, t1, func, planeta):
        resultado, evento = _calcular_ponto(t0, t1, func)

        hora_datetime = resultado.utc_datetime()[0] - timedelta(hours=3)

        localizacao = EPH['earth'] + MONTES_CLAROS
        hora_da_observacao = resultado[0]

        telescopio = localizacao.at(hora_da_observacao).observe(planeta['dados'])

        _, az, _ = telescopio.apparent().altaz()
        magnitude = planetary_magnitude(telescopio)

        return planeta['nome'], hora_datetime, evento[0], az.degrees, magnitude

    @staticmethod
    def obter_duracao_do_dia():
        meia_noite = HOJE.replace(hour=0, minute=0, second=0, microsecond=0)
        proxima_meia_noite = meia_noite + timedelta(days=1)

        t0 = TS.from_datetime(meia_noite)
        t1 = TS.from_datetime(proxima_meia_noite)

        f = almanac.sunrise_sunset(EPH, MONTES_CLAROS)

        resultado, evento = _calcular_ponto(t0, t1, f)

        diferenca = resultado[evento == 0] - resultado[evento == 1]

        hora = int(diferenca[0] * 24)
        minuto = int((diferenca[0] * 24 - hora) * 60)

        resposta = f'{hora} horas e {minuto} minutos'

        return resposta


    @staticmethod
    def obter_duracao_da_noite():
        um_dia_depois = HOJE + timedelta(days=1)

        t0 = TS.from_datetime(HOJE)
        t1 = TS.from_datetime(um_dia_depois)

        f_sol = almanac.sunrise_sunset(EPH, MONTES_CLAROS)
        f_lua = almanac.risings_and_settings(EPH, EPH['moon'], MONTES_CLAROS)

        resultado_sol, evento_sol = _calcular_ponto(t0, t1, f_sol)
        resultado_lua, evento_lua = _calcular_ponto(t0, t1, f_lua)

        diferenca_sol = resultado_sol[evento_sol == 1] - resultado_sol[evento_sol == 0]

        hora_sol = int(diferenca_sol[0] * 24)
        minuto_sol = int((diferenca_sol[0] * 24 - hora_sol) * 60)

        fase, iluminada = _calcular_fase_da_lua(t0)

        nascer_lua_dt = resultado_lua[evento_lua == 1].utc_datetime()[0]
        por_lua_dt = resultado_lua[evento_lua == 0].utc_datetime()[0]

        nasce_lua = f'{nascer_lua_dt.hour - 3:02d}:{nascer_lua_dt.minute:02d}'
        por_lua = f'{por_lua_dt.hour - 3:02d}:{por_lua_dt.minute:02d}'

        resposta = (f'{hora_sol} horas e {minuto_sol} minutos, com a Lua na fase {fase} ({iluminada}% iluminada),'
                    f' surgindo às {nasce_lua} e recolhendo-se às {por_lua}')

        return resposta

    def obter_lista_de_eventos(self):
        depois = HOJE + timedelta(hours=12)

        t0 = TS.from_datetime(HOJE)
        t1 = TS.from_datetime(depois)

        f_sol = almanac.sunrise_sunset(EPH, MONTES_CLAROS)

        resultado_sol, evento_sol = _calcular_ponto(t0, t1, f_sol)

        hora_limite_inferior = resultado_sol[evento_sol == 0][0]
        hora_limite_superior = hora_limite_inferior + timedelta(days=2)
        hora_limite_superior_planetas = hora_limite_inferior + timedelta(hours=12)

        resultado = '*Lista de planetas vísiveis*\n(Acima de 10°)\n\n'

        sequencia = []
        for planeta in self.planetas:
            f = almanac.risings_and_settings(EPH, planeta['dados'], MONTES_CLAROS, horizon_degrees=10)
            sequencia.append(self._obter_nascer_e_por(hora_limite_inferior, hora_limite_superior_planetas, f, planeta))

        sequencia_ordenada = sorted(sequencia, key=lambda x: x[1])

        for item in sequencia_ordenada:

            hora = f'{item[1].hour:02d}:{item[1].minute:02d}'

            direcao = int(item[3])

            situacao = item[2]
            if situacao == 1:
                situacao_txt = f'🔺 Depois dàs {hora}\n🧭 {direcao}°, 🌟 {item[4]:.1f}'
            else:
                situacao_txt = f'🔻 Até às {hora}\n🧭 {direcao}°, 🌟 {item[4]:.1f}'

            text = f'*{item[0]}*\n{situacao_txt}\n\n'
            resultado += text

        hora_de_sirus = self._obter_horario_de_sirius()

        resultado += hora_de_sirus

        return resultado


class Estacoes:
    estacoes = {
        0: 'Outono',
        1: 'Inverno',
        2: 'Primavera',
        3: 'Verão'
    }

    dicionario_emoji = {
        0: '🍁',
        1: '❄',
        2: '🌼',
        3: '☀'
    }

    @staticmethod
    def _estacao_atual():
        t0 = TS.utc(HOJE.year, HOJE.month, HOJE.day, HOJE.hour, HOJE.minute)
        t1 = TS.utc(HOJE.year, HOJE.month + 3, HOJE.day, HOJE.hour, HOJE.minute)
        t, y = almanac.find_discrete(t0, t1, almanac.seasons(EPH))

        time = t[0].utc_datetime()

        indice_da_estacao_atual = y[0] - 1

        if indice_da_estacao_atual == -1:
            indice_da_estacao_atual = 3

        return time, indice_da_estacao_atual

    def obter_estacao_atual(self):
        _, y = self._estacao_atual()

        if y == 2:
            preposicao = 'na'
        else:
            preposicao = 'no'

        estacao_atual = self.estacoes[y]

        emoji = self.dicionario_emoji[y]

        text = f'Estamos {preposicao} {emoji} {estacao_atual}'

        return text

    def obter_proxima_estacao(self):
        t, y = self._estacao_atual()

        diferenca = t - HOJE

        dias = diferenca.days

        if y == 3:
            preposicao = 'a'
        else:
            preposicao = 'o'

        proxima_estacao = self.estacoes[y + 1]

        return f'{dias} dias para {preposicao} {proxima_estacao}'


class Eclipse:

    @staticmethod
    def _obter_serparacao(t):
        observador = EPH['earth'] + MONTES_CLAROS

        telescopio = observador.at(t)
        sol = telescopio.observe(EPH['sun']).apparent()
        lua = telescopio.observe(EPH['moon']).apparent()

        distancia_angular = sol.separation_from(lua)

        return distancia_angular.degrees

    def obter_horario_da_lua(self):
        um_dia_depois = HOJE + timedelta(days=1)

        t0 = TS.from_datetime(HOJE)
        t1 = TS.from_datetime(um_dia_depois)

        f_lua = almanac.risings_and_settings(EPH, EPH['moon'], MONTES_CLAROS)

        resultado_lua, evento_lua = _calcular_ponto(t0, t1, f_lua)

        fase, iluminada = _calcular_fase_da_lua(t0)

        nascer_lua_dt = resultado_lua[evento_lua == 1].utc_datetime()[0] - timedelta(hours=3)
        por_lua_dt = resultado_lua[evento_lua == 0].utc_datetime()[0] - timedelta(hours=3)

        horario_nascimento = f'{nascer_lua_dt.hour:02d}:{nascer_lua_dt.minute:02d}'
        horario_por = f'{por_lua_dt.hour:02d}:{por_lua_dt.minute:02d}'

        texto = f'{fase} ({iluminada}% iluminada)'

        separacao = self._obter_serparacao(t0)

        return horario_nascimento, horario_por, texto, separacao

    def obter_dias_para_eclipse(self):
        data_do_eclipse = dt(year=2023, month=10, day=14, hour=15, minute=3, second=50, tzinfo=api.utc)

        diferenca_de_dias = data_do_eclipse - HOJE

        return diferenca_de_dias.days



if __name__ == '__main__':
    Evento().obter_lista_de_eventos()