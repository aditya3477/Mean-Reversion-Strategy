import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Mean Reversion Trading Strategy")

# User Inputs
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):", value="AAPL")
days = st.number_input("Number of Trading Days to Fetch:", min_value=10, max_value=1000, value=252, step=10)
window = st.number_input("Moving Average Window:", min_value=5, max_value=100, value=20, step=1)
std_factor = st.number_input("Bollinger Band Std Dev Factor:", min_value=1.0, max_value=3.0, value=2.0, step=0.1)

# Fetch data when the user submits
if st.button("Run Strategy"):
    with st.spinner("Fetching data..."):
        try:
            # Download stock data
            data = yf.download(symbol, period=f"{days}d", interval="1d")

            # Handle MultiIndex Columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(1)

            # Rename Close to Price for consistency
            data = data.rename(columns={"Close": "Price"})

            # Compute Bollinger Bands
            data["SMA"] = data["Price"].rolling(window=window).mean()
            data["STD"] = data["Price"].rolling(window=window).std()
            data["Upper Band"] = data["SMA"] + std_factor * data["STD"]
            data["Lower Band"] = data["SMA"] - std_factor * data["STD"]

            # Drop NaN values
            data.dropna(inplace=True)

            # Define Buy/Sell Signals
            data["Buy Signal"] = data["Price"] < data["Lower Band"]
            data["Sell Signal"] = data["Price"] > data["Upper Band"]

            # Plot Results
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(data.index, data["Price"], label="Stock Price", color="blue")
            ax.plot(data.index, data["Upper Band"], label="Upper Bollinger Band", linestyle="--", color="red")
            ax.plot(data.index, data["Lower Band"], label="Lower Bollinger Band", linestyle="--", color="green")
            ax.scatter(data.index[data["Buy Signal"]], data["Price"][data["Buy Signal"]], label="Buy Signal", marker="^", color="green", alpha=1)
            ax.scatter(data.index[data["Sell Signal"]], data["Price"][data["Sell Signal"]], label="Sell Signal", marker="v", color="red", alpha=1)
            ax.legend()
            ax.set_title(f"Mean Reversion Strategy for {symbol}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Stock Price")

            # Show Plot in Streamlit
            st.pyplot(fig)

            # Strategy Performance Summary
            initial_price = data["Price"].iloc[0]
            final_price = data["Price"].iloc[-1]
            returns = ((final_price - initial_price) / initial_price) * 100
            st.subheader("Strategy Performance")
            st.write(f"Initial Price: {initial_price:.2f}")
            st.write(f"Final Price: {final_price:.2f}")
            st.write(f"Strategy Return: {returns:.2f}%")

            # Download Data as CSV
            csv = data.to_csv().encode('utf-8')
            st.download_button("Download Data", data=csv, file_name=f"{symbol}_mean_reversion.csv", mime="text/csv")
        
        except Exception as e:
            st.error(f"Error fetching stock data: {e}")
