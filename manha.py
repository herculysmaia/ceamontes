from mensagens import Mensagens

mensageiro = Mensagens()
mensagem = mensageiro.mensagem_manha()

txt = mensagem['mensagem']
utf = txt.encode('utf-8')

with open('saida.txt', 'wb') as arq:
    arq.write(utf)
