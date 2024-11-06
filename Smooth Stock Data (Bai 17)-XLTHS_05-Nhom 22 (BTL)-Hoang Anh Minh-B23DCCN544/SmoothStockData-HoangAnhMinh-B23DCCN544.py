import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from vnstock import stock_historical_data
import numpy as np
import pandas as pd
from tkinter import messagebox



def PlotSmoothedData():
    graph.clear()
    if interval.get()!="1" and interval.get()!="5" and interval.get()!="15" and interval.get()!="30" and interval.get()!=" 1H" and interval.get()!="1D":
        messagebox.showerror("Format error", "Program dont have that interval, try: \n1: 1 minutes\n5: 5 minutes\n15: 15 minutes\n30: 30 minutes\n1H: 1 hour\n1D: 1 day")
        return 0
    stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')
    original_length = len(stock)

    if (interval.get()=="1" or interval.get()=="5" or interval.get()=="15" or interval.get()=="30" or interval.get()=="1H") and start_date.get() !=str(stock['time'][0]) :
        start_date.set(str(stock['time'][0][0:10]))
        messagebox.showinfo("Notice","1, 5, 15, 30, 1H intervals can only get data 90 days before the End date, cant go any further back.\nOnly 1D interval can go further than 90 days.")



    if original_length<2:
        messagebox.showerror("No data error","No data in this time frame" )

    print(stock)
    stock['close'] = pd.to_numeric(stock['close'], downcast='integer', errors='coerce')
    original_data = stock[['close']].values.squeeze()


    original_data=add_more_data_to_original(original_data)

    graph.plot(stock['time'], stock[['close']], label='Original Data', color='b')

    if Using_amplitude_thresholding.get()==1:
        smoothed_data = amplitude_thresholding(original_data, original_length)
        smoothed_data= reconstruct_original(smoothed_data,original_length)
        graph.plot(stock['time'], smoothed_data.real, label='Amplitude Thresholding', color='r')

    if Using_frequency_cutoff.get()==1:
        smoothed_data = frequency_cutoff(original_data, original_length)
        smoothed_data = reconstruct_original(smoothed_data, original_length)
        graph.plot(stock['time'], smoothed_data.real, label='Frequency Cutoff', color='g')
    graph.legend()
    canvas.draw()
    Amount_of_Data.config(text=str(len(stock)))


def add_more_data_to_original(original_data):
    original_length=len(original_data)
    temp = np.empty(0)
    for i in range(0, int(original_length / 2), 1):
        temp = np.append(temp, original_data[0])
    for i in range(0, original_length, 1):
        temp = np.append(temp, original_data[i])
    for i in range(0, int(original_length / 2), 1):
        temp = np.append(temp, original_data[len(original_data) - 1])
    return temp

def reconstruct_original(smoothed_data, original_length):
    temp = np.empty(0)
    for i in range(int( original_length/ 2), original_length + int(original_length / 2), 1):
        temp = np.append(temp, smoothed_data[i])
    return temp

def amplitude_thresholding(original_data, original_length):
    data_length=len(original_data)

    temp = np.empty(0)
    fft_data = np.fft.fft(original_data)

    if using_custom_threshold.get()==0:
        for i in range(0, data_length,1):
            temp=np.append(temp,np.abs(fft_data[i]))
        sorted_fft_data=np.sort(temp)
        if original_length<50:
            threshold = sorted_fft_data[data_length - 1 - 2]
        elif original_length<100:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 10)]
        elif original_length<250:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 75)]
        elif original_length<500:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 90)]
        elif original_length<1000:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 150)]
        elif original_length<2500:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 300)]
        elif original_length<5000:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 500)]
        else:
            threshold = sorted_fft_data[data_length - 1 - int(original_length / 1000)]
    else:
        threshold=custom_threshold.get()

    print("threshold:",np.abs(threshold))
    fft_data[np.abs(fft_data) < np.abs(threshold)] = 0
    smoothed = np.fft.ifft(fft_data)
    return smoothed

def frequency_cutoff(original_data, original_length):
    if using_custom_cutoff_frequency.get()==0:
        cutoff_frequency=2/original_length
    else:
        cutoff_frequency=custom_cutoff_frequency.get()
    fft_data = np.fft.fft(original_data)
    frequencies = np.fft.fftfreq(len(original_data))
    print("cutoff freq:", cutoff_frequency)
    fft_data[np.abs(frequencies) > cutoff_frequency] = 0
    smoothed= np.fft.ifft(fft_data)
    return smoothed

root = tk.Tk()

start_date = tk.StringVar(root, "2023-09-02")
end_date = tk.StringVar(root, "2024-11-04")
stock_symbol = tk.StringVar(root, "BID")
interval = tk.StringVar(root, "1D")

Using_amplitude_thresholding=tk.IntVar(root, 1)
Using_frequency_cutoff=tk.IntVar(root,1)

using_custom_threshold=tk.IntVar(root,0)
using_custom_cutoff_frequency=tk.IntVar(root, 0)

custom_threshold=tk.DoubleVar(root,20000)
custom_cutoff_frequency=tk.DoubleVar(root, 0.01)
stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')
stock['close'] = pd.to_numeric(stock['close'], downcast='integer', errors='coerce')

fig = Figure(figsize=(10, 3.5))
graph = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)

canvas.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()
root.geometry("1000x600")

root.title("Smooth Stock Data - HOANG ANH MINH-B23DCCN544")




frame = tk.Frame(root)
frame.columnconfigure(0)
frame.columnconfigure(1)
frame.columnconfigure(2)
frame.columnconfigure(3)

Amount_of_Data_Label=tk.Label(master=frame, text="Amount of point in graph:",font=("Times New Roman", 12))
Amount_of_Data_Label.grid(column=1, row=0, sticky="e")

Amount_of_Data = tk.Label(master=frame, text=str(len(stock)),font=("Times New Roman", 12))
Amount_of_Data.update()
Amount_of_Data.grid(column=2, row=0, sticky="w")

Amplitude_thresholding_Checkbutton=tk.Checkbutton(master=frame,text="Amplitude Thresholding", variable=Using_amplitude_thresholding, onvalue=1, offvalue=0, font=("Times New Roman", 12))
Amplitude_thresholding_Checkbutton.grid(column=0, row=1)

Frequency_cutoff_Checkbutton=tk.Checkbutton(master=frame,text="Frequency Cutoff", variable=Using_frequency_cutoff, onvalue=1, offvalue=0, font=("Times New Roman",12))
Frequency_cutoff_Checkbutton.grid(column=2, row=1)

Start_date_Label = tk.Label(master=frame, text="Start date:", font=("Times New Roman", 12))
Start_date_Label.grid(column=0, row=2, sticky="w")

Start_date_Input = tk.Entry(master=frame, textvariable=start_date)
Start_date_Input.grid(column=1, row=2)

End_date_Label = tk.Label(master=frame, text="End date:", font=("Times New Roman", 12))
End_date_Label.grid(column=0, row=3, sticky="w")

End_date_Input = tk.Entry(master=frame, textvariable=end_date)
End_date_Input.grid(column=1, row=3)

Stock_symbol_Label = tk.Label(master=frame, text="Stock symbol:", font=("Times New Roman", 12))
Stock_symbol_Label.grid(column=2, row=2, sticky="w")

Stock_symbol_Input = tk.Entry(master=frame, textvariable=stock_symbol)
Stock_symbol_Input.grid(column=3, row=2)

Interval_Label = tk.Label(master=frame, text="Interval:", font=("Times New Roman", 12))
Interval_Label.grid(column=2, row=3, sticky="w")

Interval_Input = tk.Entry(master=frame, textvariable=interval)
Interval_Input.grid(column=3, row=3)

Custom_threshold_Checkbutton = tk.Checkbutton(master=frame, text="Using custom threshold",font=("Times New Roman", 12), variable=using_custom_threshold, onvalue=1, offvalue=0, fg="red")
Custom_threshold_Checkbutton.grid(column=1, row=4, sticky="w")

Custom_cutoff_frequency_Checkbutton = tk.Checkbutton(master=frame, text="Using custom cutoff frequency",font=("Times New Roman", 12), variable=using_custom_cutoff_frequency, onvalue=1, offvalue=0, fg="green")
Custom_cutoff_frequency_Checkbutton.grid(column=1, row=5, sticky="w")

Custom_threshold_Input=tk.Entry(master=frame, textvariable=custom_threshold)
Custom_threshold_Input.grid(column=2, row=4, sticky="w")

Custom_cutoff_frequency_Input=tk.Entry(master=frame, textvariable=custom_cutoff_frequency)
Custom_cutoff_frequency_Input.grid(column=2, row=5, sticky="w")
frame.pack()

confirm_button = tk.Button(master=root, text="Confirm", command=PlotSmoothedData, font=("Times New Roman", 12))
confirm_button.pack()

PlotSmoothedData()
root.mainloop()