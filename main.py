from flask import Flask, render_template, request
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
import pytz
import time

app = Flask(__name__)

@app.route("/", methods=["GET", " "POST"])
def index():
    resultado = None
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        par = request.form["par"]
        direcao = request.form["direcao"].lower()
        horario = request.form["horario"]
        dias = int(request.form["dias"])

        try:
            iq = IQ_Option(email, senha)
            iq.connect()
            iq.change_balance("PRACTICE")
            if not iq.check_connect():
                resultado = "Erro ao conectar."
            else:
                timezone = pytz.timezone("America/Sao_Paulo")
                hoje = datetime.now(timezone).date()
                resultados = []

                for dias_atras in range(1, dias + 1):
                    data = hoje - timedelta(days=dias_atras)
                    hora, minuto = map(int, horario.split(":"))
                    dt_local = timezone.localize(datetime(data.year, data.month, data.day, hora, minuto))
                    dt_utc = dt_local.astimezone(pytz.utc)

                    timestamp = int(dt_utc.timestamp())
                    candles = iq.get_candles(par, 60, 1, timestamp)
                    if candles:
                        candle = candles[0]
                        open_price = round(candle["open"], 5)
                        close_price = round(candle["close"], 5)
                        if open_price == close_price:
                            res = "DOJI"
                        elif close_price > open_price and direcao == "call":
                            res = "WIN"
                        elif close_price < open_price and direcao == "put":
                            res = "WIN"
                        else:
                            res = "LOSS"
                        resultados.append(f"{data.isoformat()} - {res}")
                    else:
                        resultados.append(f"{data.isoformat()} - SEM DADOS")
                    time.sleep(1)

                resultado = "\n".join(resultados)
        except Exception as e:
            resultado = f"Erro: {str(e)}"

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
