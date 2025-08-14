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

        # Download historical data
        df1 = yf.download(symbol1, period=period)
        df2 = yf.download(symbol2, period=period)

        # Join close prices and calculate percent change
        joined_df = df1['Close'].join(df2['Close'], lsuffix=f"_{symbol1}", rsuffix=f"_{symbol2}").dropna()
        returns = joined_df.pct_change().dropna()

        # Make sure we have enough data for rolling window
        if len(returns) < window:
            return jsonify({"error": f"Not enough data for the rolling window of {window} days."}), 400

        # Calculate rolling correlation
        corr = returns.iloc[:, 0].rolling(f"{window}d").corr(returns.iloc[:, 1])
        corr = corr.dropna()

        # Prepare response
        return jsonify({
            "dates": corr.index.strftime('%Y-%m-%d').tolist(),
            "correlation": corr.tolist()
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
