import talib
from talib import abstract
import pandas as pd
import flask
from flask import Flask, request, redirect, render_template, session
import flask_session
from flask_session import Session 
import patterns
from patterns import patterns
import yfinance as yf
import os
import numpy as np
import csv


screener=Flask(__name__, template_folder="template",static_folder="static", static_url_path="/")


@screener.route('/', methods=["GET","POST"])
def index():
    pat = request.args.get("candle", None)
    stocks={}
    with open("datasets/comp.csv") as file:
        for j in csv.reader(file):
            stocks[j[0]]={"company":j[1]}   

    if not os.path.exists("datasets/compd"):
        os.makedirs("datasets/compd")
    datafile = os.listdir("datasets/compd")

    available_symbols = {filename.split(".")[0] for filename in datafile}

    # 2. Create a list of keys you want to REMOVE
    #    (We must list them first to avoid the modification error)
    keys_to_remove = [symbol for symbol in stocks if symbol not in available_symbols]

    # 3. Delete the invalid keys safely
    for symbol in keys_to_remove:
        del stocks[symbol]

    # stocks now only contains keys that exist in your datafiles
    if pat:
        for i in datafile:
                try:
                    symb=i.split(".")[0]
                    # 1. Read CSV
                    dat = pd.read_csv("datasets/compd/{}".format(i), header=[0, 1], index_col=0)
                    dat.columns = dat.columns.get_level_values(0)
                    
                    # 2. Clean Data (Remove the "Date" row with empty values)
                    dat.dropna(inplace=True)
                    
                    # 3. CRITICAL FIX: Skip Empty Files
                    # If the file was empty (like ATVI) or became empty after dropna(), skip it.
                    # if dat.empty:
                    #     print(f"Skipping {i}: Dataframe is empty.")
                    #     os.remove('datasets/compd/{}'.format(i))
                    #     print(f"Removing {i}: Dataframe is empty.")                   
                    #     continue

                    # 4. Prepare Inputs safely
                    # use np.ascontiguousarray for 'volume' to prevent memory crashes
                    inputs = {
                        "open": dat["Open"].to_numpy(dtype="double"),
                        "high": dat["High"].to_numpy(dtype="double"),
                        "low": dat["Low"].to_numpy(dtype="double"),
                        "close": dat["Close"].to_numpy(dtype="double"),
                        "volume": np.ascontiguousarray(dat["Volume"].to_numpy(dtype="double"))
                    }

                    
                    # 5. Execute Pattern
                    # using abstract.Function is safer than getattr
                    # func = abstract.Function(pat)
                    # res = func(inputs)
                    # # print(res)
                    
                    # Check if the pattern name exists in TA-Lib before calling
                    if hasattr(abstract, pat):
                        res = getattr(abstract, pat)(inputs)
                        dat[f'result{i}and{pat}']=res[-1]
                        # print(dat[f'result{i}and{pat}'])
                        # print(dat[dat[f'result{i}and{pat}']!=0])                
                    else:
                        print(f"Warning: Pattern '{pat}' not found in TA-Lib.")
                        continue  

                    if res[-1]> 0:
                        stocks[symb][pat] = "Bullish"
                    elif res[-1] <0:
                        stocks[symb][pat] = "Bearish"
                    else:
                        stocks[symb][pat] = "Neutral"
                    print(stocks)
            
                except Exception as e:
                    print(f"failed on {i}: {e}")
            
    return render_template('index.html', patterns=patterns, stocks= stocks, cur_pattern=pat)




@screener.route("/snapshot")
def snapshot():
    with open("datasets/comp.csv") as file:
        sym=file.read().splitlines()
        for i in sym:
            sym1=i.split(',')[0]
            daf=yf.download(sym1, start="2020-01-01", end="2026-01-01")
            daf.to_csv('datasets/compd/{}.csv'.format(sym1))

    return ""


if __name__=="__main__":
    screener.run(debug=True)