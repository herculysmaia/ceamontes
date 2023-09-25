from flask import Flask, jsonify, render_template

from mensagens import gerenciador_mensagens  # Importando o módulo gerenciador_mensagens

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("index.html")


@app.route('/manha')
def mensagem_manha():
    mensagem = gerenciador_mensagens.mensagem_manha()

    return jsonify(mensagem)


@app.route('/tarde')
def mensagem_tarde():
    mensagem = gerenciador_mensagens.mensagem_tarde()

    return jsonify(mensagem)


if __name__ == '__main__':
    app.run(debug=True)
