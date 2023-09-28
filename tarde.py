from mensagens import Mensagens

mensageiro = Mensagens()
mensagem = mensageiro.mensagem_tarde()
lista = mensageiro.lista_de_eventos()

txt = mensagem['mensagem']
lis = lista['mensagem']

txt_utf = txt.encode('utf-8')
lis_utf = lis.encode('utf-8')

with open('saida.txt', 'wb') as arq:
    arq.write(txt_utf)

with open('lista.txt', 'wb') as arq:
    arq.write(lis_utf)
