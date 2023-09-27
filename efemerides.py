from skyfield import api, almanac
from datetime import datetime as dt, timedelta

from skyfield.framelib import ecliptic_frame

TS = api.load.timescale()
EPH = api.load('de421.bsp')

HOJE = dt.now(tz=api.utc) + timedelta(minutes=15)


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

    montes_claros = api.wgs84.latlon(16.715767 * api.S, 43.863275 * api.W)

    def __init__(self):
        super().__init__()

    @staticmethod
    def _calcular_ponto(t0, t1, f):
        t, y = almanac.find_discrete(t0, t1, f)

        return t, y

    @staticmethod
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

    def obter_duracao_do_dia(self):
        meia_noite = HOJE.replace(hour=0, minute=0, second=0, microsecond=0)
        proxima_meia_noite = meia_noite + timedelta(days=1)

        t0 = TS.from_datetime(meia_noite)
        t1 = TS.from_datetime(proxima_meia_noite)

        f = almanac.sunrise_sunset(EPH, self.montes_claros)

        resultado, evento = self._calcular_ponto(t0, t1, f)

        diferenca = resultado[evento == 0] - resultado[evento == 1]

        hora = int(diferenca[0] * 24)
        minuto = int((diferenca[0] * 24 - hora) * 60)

        resposta = f'{hora} horas e {minuto} minutos'

        return resposta

    def obter_duracao_da_noite(self):
        um_dia_depois = HOJE + timedelta(days=1)

        t0 = TS.from_datetime(HOJE)
        t1 = TS.from_datetime(um_dia_depois)

        f_sol = almanac.sunrise_sunset(EPH, self.montes_claros)
        f_lua = almanac.risings_and_settings(EPH, EPH['moon'], self.montes_claros)

        resultado_sol, evento_sol = self._calcular_ponto(t0, t1, f_sol)
        resultado_lua, evento_lua = self._calcular_ponto(t0, t1, f_lua)

        diferenca_sol = resultado_sol[evento_sol == 1] - resultado_sol[evento_sol == 0]

        hora_sol = int(diferenca_sol[0] * 24)
        minuto_sol = int((diferenca_sol[0] * 24 - hora_sol) * 60)

        fase, iluminada = self._calcular_fase_da_lua(t0)

        nascer_lua_dt = resultado_lua[evento_lua == 1].utc_datetime()[0]
        por_lua_dt = resultado_lua[evento_lua == 0].utc_datetime()[0]

        nasce_lua = f'{nascer_lua_dt.hour - 3:02d}:{nascer_lua_dt.minute:02d}'
        por_lua = f'{por_lua_dt.hour - 3:02d}:{por_lua_dt.minute:02d}'

        resposta = (f'{hora_sol} horas e {minuto_sol} minutos, com a Lua na fase {fase} ({iluminada}% iluminada),'
                    f' surgindo às {nasce_lua} e recolhendo-se às {por_lua}')

        return resposta


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
