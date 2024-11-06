import tkinter as tk

import math
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

from vnstock import stock_historical_data
import numpy as np
import pandas as pd


def PlotSmoothedData():
    graph.clear()

    stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')
    stock['close'] = pd.to_numeric(stock['close'], downcast='integer', errors='coerce')
    original_data = stock[['close']].values.squeeze()
    length=len(original_data)
    #Construct
    temp=np.empty(0)
    for i in range(0, int(length/2),1):
        temp=np.append(temp,original_data[0])
    for i in range(0, len(original_data),1):
        temp = np.append(temp, original_data[i])
    for i in range(0, int(length/2),1):
        temp=np.append(temp,original_data[len(original_data)-1])
    original_data=temp
    print(temp)
    print(len(stock))
    graph.plot(stock['time'], stock[['close']], label='Original Data', color='b')

    if AM==1:
        smoothed_data1 = amplitude_thresholding(original_data)
        #Recontruct
        temp2=np.empty(0)
        for i in range(int(length/2),length+int(length/2),1):
            temp2=np.append(temp2, smoothed_data1[i])
        smoothed_data1=temp2
        graph.plot(stock['time'], smoothed_data1.real, label='Amplitude Thresholding', color='r')
        print(smoothed_data1.shape)
    if FC==1:
        smoothed_data= frequency_cutoff(original_data)
        #graph.plot(stock['time'], smoothed_data.real, label='Frequency Cutoff', color='y')
        print(smoothed_data.shape)
    graph.legend()
    canvas.draw()

    Amount_of_Data.config(text=str(len(stock)))


def amplitude_thresholding(original_data):
    data_length=len(original_data)
    print(data_length)
    a = np.empty(0)
    fft_data = np.fft.fft(original_data)


    print("a:",a)

    for i in range(0, data_length,1):
        a=np.append(a,np.abs(fft_data[i]))
        print(np.abs(fft_data[i]))
    sorted_fft_data=np.sort(a)
    print("s:",sorted_fft_data)
    print(len(sorted_fft_data))
    """
    ex =0
    while 50*pow(2, ex)<data_length and 50*pow(2,ex+1)<data_length:
        ex=ex+1

    threshold=sum/data_length*pow(math.e,ex)/10
    print(threshold, sum/data_length, sum)
    """
    """
    if data_length<62:
        threshold=15625
    elif data_length<125:
        threshold=31250
    elif data_length<250:
        threshold=62500
    elif data_length<500:
        threshold=125000
    elif data_length<1000:
        threshold=250000
    else:
        threshold=500000
    """
    print()
    threshold=sorted_fft_data[data_length-1-25]
    print("t:",threshold)
    fft_data[np.abs(fft_data) < 3000000] = 0
    smoothed = np.fft.ifft(fft_data)
    return smoothed

def frequency_cutoff(original_data):
    fft_data = np.fft.fft(original_data)
    print(fft_data)
    frequencies = np.fft.fftfreq(len(original_data))
    fft_data[np.abs(frequencies) > 0.015] = 0
    smoothed= np.fft.ifft(fft_data)
    return smoothed

root = tk.Tk()

start_date = tk.StringVar(root, "2014-10-02")
end_date = tk.StringVar(root, "2024-11-04")
stock_symbol = tk.StringVar(root, "FPT")
interval = tk.StringVar(root, "1D")
AM=1
FC=0
stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')
stock['close'] = pd.to_numeric(stock['close'], downcast='integer', errors='coerce')


fig = Figure(figsize=(10, 4))
graph = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)

canvas.draw()
canvas.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()
root.geometry("1000x600")

root.title("HOANG ANH MINH")

# label=tk.Label(master=root,text="Graph",font=("Times New Roman", 18))
# label.pack(padx=10, pady=20)

frame = tk.Frame(root)
frame.columnconfigure(0)
frame.columnconfigure(1)
frame.columnconfigure(2)
frame.columnconfigure(3)

Start_date_Label = tk.Label(master=frame, text="Start date", font=("Times New Roman", 18))
Start_date_Label.grid(column=0, row=0)

Start_date_Input = tk.Entry(master=frame, textvariable=start_date)
Start_date_Input.grid(column=1, row=0)

End_date_Label = tk.Label(master=frame, text="End date", font=("Times New Roman", 18))
End_date_Label.grid(column=0, row=1)

End_date_Input = tk.Entry(master=frame, textvariable=end_date)
End_date_Input.grid(column=1, row=1)

Stock_symbol_Label = tk.Label(master=frame, text="Stock symbol", font=("Times New Roman", 18))
Stock_symbol_Label.grid(column=2, row=0)

Stock_symbol_Input = tk.Entry(master=frame, textvariable=stock_symbol)
Stock_symbol_Input.grid(column=3, row=0)

Interval_Label = tk.Label(master=frame, text="Interval", font=("Times New Roman", 18))
Interval_Label.grid(column=2, row=1)

Interval_Input = tk.Entry(master=frame, textvariable=interval)
Interval_Input.grid(column=3, row=1)
frame.pack()

confirm_button = tk.Button(master=root, text="Confirm", command=PlotSmoothedData)
confirm_button.pack()

Amount_of_Data = tk.Label(master=root, text=str(len(stock)))
Amount_of_Data.pack()
PlotSmoothedData()
root.mainloop()