from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route("/correlation", methods=["POST"])
def rolling_correlation():
    try:
        data = request.get_json()

        symbol1 = data.get("symbol1", "").upper()
        symbol2 = data.get("symbol2", "").upper()
        window = int(data.get("window", 30))
        period = data.get("period", "1y")

        if not symbol1 or not symbol2:
            return jsonify({"error": "Missing symbols"}), 400

        # Download data
        df1 = yf.download(symbol1, period=period)["Adj Close"]
        df2 = yf.download(symbol2, period=period)["Adj Close"]

        # Combine and clean
        df = pd.DataFrame({symbol1: df1, symbol2: df2}).dropna()

        if df.empty:
            return jsonify({"error": "No overlapping data found for the selected period"}), 400

        if window > len(df):
            return jsonify({"error": f"Rolling window ({window}) is larger than data length ({len(df)})"}), 400

        # Compute correlation
        correlation = df[symbol1].rolling(window).corr(df[symbol2])

        return jsonify({
            "dates": df.index.strftime('%Y-%m-%d').tolist(),
            "correlation": correlation.tolist()
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

