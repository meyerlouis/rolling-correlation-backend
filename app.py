from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/correlation", methods=["POST"])
def correlation():
    data = request.json
    symbol1 = data["symbol1"]
    symbol2 = data["symbol2"]
    window = int(data["window"])
    period = data["period"]

    try:
        df1 = yf.download(symbol1, period=period)
        df2 = yf.download(symbol2, period=period)

        if df1.empty or df2.empty:
            return jsonify({"error": "Invalid ticker(s) or no data found"}), 400

        df = pd.DataFrame({
            symbol1: df1["Adj Close"],
            symbol2: df2["Adj Close"]
        }).dropna()

        rolling_corr = df[symbol1].rolling(window).corr(df[symbol2])

        return jsonify({
            "dates": df.index.strftime("%Y-%m-%d").tolist(),
            "correlation": rolling_corr.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
