from skyfield import api, almanac
from datetime import datetime as dt, timezone, timedelta

TS = api.load.timescale()
EPH = api.load('de421.bsp')

deslocamento_brasilia = timedelta(hours=-3)
TZ = timezone(deslocamento_brasilia)

agora = dt.now() + timedelta(minutes=15)
HOJE = agora.replace(tzinfo=TZ)


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
        inicio_do_ano = dt(HOJE.year, 1, 1, tzinfo=TZ)
        diferenca = HOJE - inicio_do_ano
        return diferenca.days

    @staticmethod
    def dias_no_ano():
        inicio_do_ano = dt(HOJE.year, 1, 1, tzinfo=TZ)
        fim_do_ano = dt(HOJE.year + 1, 1, 1, tzinfo=TZ)
        diferenca = fim_do_ano - inicio_do_ano
        return diferenca.days

    @staticmethod
    def dias_final_de_ano():
        fim_do_ano = dt(HOJE.year, 12, 31, tzinfo=TZ)
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
