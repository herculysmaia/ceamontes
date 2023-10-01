from mensagens import Mensagens

mensageiro = Mensagens()
mensagem = mensageiro.eclipse()

txt = mensagem['mensagem']
utf = txt.encode('utf-8')

with open('eclipse.txt', 'wb') as arq:
    arq.write(utf)
