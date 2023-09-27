import clima
import efemerides


class Astro:
    calendario = efemerides.Calendario()
    estacoes = efemerides.Estacoes()
    evento = efemerides.Evento()

    dia_de_hoje = calendario.dia_de_hoje()

    dia_ano = calendario.dia_ano()
    dias_no_ano = calendario.dias_no_ano()
    dias_final_de_ano = calendario.dias_final_de_ano()

    comemorativa = calendario.comemorativa()

    proxima_estacao = estacoes.obter_proxima_estacao()
    estacao_atual = estacoes.obter_estacao_atual()

    duracao_do_dia = evento.obter_duracao_do_dia()
    duracao_da_noite = evento.obter_duracao_da_noite()


class Clima:
    condicao_noite = clima.condicao_noite()
    condicao_atual = clima.condicao_atual()
    temperatura_minima = clima.temperatura_minima()
    temperatura_maxima = clima.temperatura_maxima()
    temperatura = clima.temperatura_atual()
    umidade = clima.umidade_atual()
    chance_de_chuva = clima.obter_chance_de_chuva()
    visibilidade = clima.visibilidade_atual()


class Mensagens:
    @staticmethod
    def mensagem_manha():
        clima_atual = Clima()
        astronomia = Astro()

        condicao = clima_atual.condicao_atual
        temperatura = clima_atual.temperatura
        temperatura_maxima = clima_atual.temperatura_maxima
        umidade = clima_atual.umidade
        chance_de_chuva = clima_atual.chance_de_chuva
        visibilidade = clima_atual.visibilidade

        dia_de_hoje = astronomia.dia_de_hoje

        dia_ano = astronomia.dia_ano
        dias_no_ano = astronomia.dias_no_ano
        comemorativa = astronomia.comemorativa

        estacao = astronomia.estacao_atual
        proxima_estacao = astronomia.proxima_estacao
        dias_final_do_ano = astronomia.dias_final_de_ano

        horas_de_sol = astronomia.duracao_do_dia

        texto_mensagem = (
            '🌄 * Bom dia! *\n\n'
            f'Montes Claros, {dia_de_hoje} ({dia_ano} / {dias_no_ano}). {comemorativa}\n\n'
            f'O Sol acaba de nascer e está fazendo {temperatura}°C com a condição do clima de {condicao}. A umidade '
            f'relativa do ar é de {umidade}%, {chance_de_chuva}. A cobertura de nuvens está em {visibilidade}% e a '
            f'temperatura máxima prevista para hoje é de {temperatura_maxima}°C.\n\n' 
            f'{estacao} e teremos {horas_de_sol} de luz solar disponível.\n\n'
            f'Faltam {proxima_estacao} e {dias_final_do_ano} dias para o ano acabar.'
        )

        return {'mensagem': texto_mensagem}

    @staticmethod
    def mensagem_tarde():
        clima_atual = Clima()
        astronomia = Astro()

        condicao_clima = clima_atual.condicao_noite
        temperatura_minima = clima_atual.temperatura_minima

        hora_duracao_noite = astronomia.duracao_da_noite

        fenomenos = 'Lista de eventos em constução'

        texto_mensagem = (
            '📸 O Sol irá se pôr em aproximadamente meia hora, uma oportunidade perfeita para capturar aquela foto de '
            'fim de tarde. Vai deixar essa chance passar? Não se preocupe! Confira a lista de eventos astronômicos '
            f'programados para as próximas horas. Fique atento! A noite promete durar {hora_duracao_noite}. A previsão '
            f'meteorológica para as 20h aponta para {condicao_clima}. A temperatura mínima esperada é de '
            f'{temperatura_minima}°C.\n\n{fenomenos}'
        )

        return {'mensagem': texto_mensagem}


gerenciador_mensagens = Mensagens()
