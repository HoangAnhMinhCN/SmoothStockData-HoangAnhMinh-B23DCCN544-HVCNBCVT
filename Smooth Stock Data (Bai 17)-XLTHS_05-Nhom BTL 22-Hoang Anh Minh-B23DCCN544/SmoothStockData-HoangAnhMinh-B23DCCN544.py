import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from vnstock import stock_historical_data
import numpy as np
from tkinter import messagebox


#Maker: Hoang Anh Minh - B23DCCN544 - HVCNBCVT
#Nhom XLTHS 05, nhom bai tap lon: nhom 22 - Thanh vien: Hoang Anh Minh
#Bai tap lon XLTHS, bai 17: su dung DSP lam muot du lieu chung khoan

#Credit:
# https://github.com/thinh-vu/vnstock
# https://lutpub.lut.fi/bitstream/handle/10024/164024/kandityo_Pauli_Anttonen.pdf?sequence=3&isAllowed=y


# Plot the graphs
def PlotSmoothedData():
    graph.clear()
    # Thong bao loi viet sai Interval
    if interval.get() != "1" and interval.get()!="3" and interval.get() != "5" and interval.get() != "15" and interval.get() != "30" and interval.get() != "1H" and interval.get() != "1D":
        messagebox.showerror("Format error",
                             "Program dont have that interval, try: \n1: 1 minutes\n3: 3 minutes\n5: 5 minutes\n15: 15 minutes\n30: 30 minutes\n1H: 1 hour\n1D: 1 day")
        return 0

    # Lay du lieu chung khoan bang vnstock (credit: https://github.com/thinh-vu/vnstock)
    try:
        stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')
    except:
        messagebox.showerror("Error", "Cant get stock data. Please check the time frame, its format and stock symbol.\nOr the program doesnt have that stock")
        return 0
    print(stock)
    original_length = len(stock)
    print("Data length:", original_length)

    # Thong bao loi khong co du lieu trong khoang thoi gian duoc xet
    if original_length < 2:
        messagebox.showerror("No data error", "No data in this time frame")
        return 0

    # Chuyen data shape tu (n,1) sang (n, ), tu pandas dataframe sang numpy ndarray
    original_data = stock[['close']].values.squeeze()
    original_data = add_more_data_to_original(original_data)

    # Ve do thi du lieu goc
    graph.plot(stock['time'], stock[['close']], label='Original Data', color='b')

    # Chon su dung Amplitude Thresholding hay Frequency Cutoff hay ca hai
    if Using_amplitude_thresholding.get() == 1:
        smoothed_data = amplitude_thresholding(original_data, original_length)
        smoothed_data = reconstruct_original(smoothed_data, original_length)
        graph.plot(stock['time'], smoothed_data.real, label='Amplitude Thresholding', color='r')

    if Using_frequency_cutoff.get() == 1:
        smoothed_data = frequency_cutoff(original_data, original_length)
        smoothed_data = reconstruct_original(smoothed_data, original_length)
        graph.plot(stock['time'], smoothed_data.real, label='Frequency Cutoff', color='g')
    #Ve do thi
    graph.legend()
    canvas.draw()
    Amount_of_Data.config(text=str(len(stock)))
    print("Plotting completed")


# -Cho them du lieu co gia tri bang du lieu dau tien va du lieu cuoi vao dau va vao cuoi du lieu goc,
# de khi ve do thi cua du lieu duoc lam muot, phan cuoi va phan dau cua du lieu duoc lam muot giong voi du lieu goc
def add_more_data_to_original(original_data):
    original_length = len(original_data)
    temp = np.empty(0)
    for i in range(0, int(original_length / 2), 1):
        temp = np.append(temp, original_data[0])
    for i in range(0, original_length, 1):
        temp = np.append(temp, original_data[i])
    for i in range(0, int(original_length / 2), 1):
        temp = np.append(temp, original_data[len(original_data) - 1])
    return temp


# Loai bo du lieu thua duoc them vao
def reconstruct_original(smoothed_data, original_length):
    temp = np.empty(0)
    for i in range(int(original_length / 2), original_length + int(original_length / 2), 1):
        temp = np.append(temp, smoothed_data[i])
    return temp

#Loc bang phuong phap Amplitude Thresholding
def amplitude_thresholding(original_data, original_length):
    data_length = len(original_data)

    # Fourier tranformation cua du lieu goc
    fft_data = np.fft.fft(original_data)

    # Chon gioi han (threshold) phu hop
    if using_custom_threshold.get() == 0:
        # My algorithm
        temp = np.empty(0)
        for i in range(0, data_length, 1):
            temp = np.append(temp, np.abs(fft_data[i]))
        sorted_fft_data = np.sort(temp)
        threshold = sorted_fft_data[data_length - 1 - int(np.log(data_length))]
    else:  # Hoac tu chon Threshold mong muon cua minh
        threshold = custom_threshold.get()
    print("threshold:", np.abs(threshold))

    # Tat ca bien do ma nho hon Threshold thi se bang 0
    fft_data[np.abs(fft_data) < np.abs(threshold)] = 0
    # Chuyen ve mien thuc
    smoothed = np.fft.ifft(fft_data)
    print("Data processing using Amplitude Thresholding completed.")
    return smoothed

#Loc bang phuong phap Frequency Cutoff
def frequency_cutoff(original_data, original_length):
    # Chon tan so cat
    if using_custom_cutoff_frequency.get() == 0:
        # My algorithm
        cutoff_frequency = np.e / original_length
    else:  # Hoac tu chon tan so cat mong muon
        cutoff_frequency = custom_cutoff_frequency.get()
    # Fourier tranformation cua du lieu goc
    fft_data = np.fft.fft(original_data)
    frequencies = np.fft.fftfreq(len(original_data))
    print("cutoff frequency:", cutoff_frequency)

    # Tat ca cac tan so ma lon hon tan so cat deu bang 0
    fft_data[np.abs(frequencies) > cutoff_frequency] = 0
    # Chuyen ve mien thuc
    smoothed = np.fft.ifft(fft_data)
    print("Data processing using Frequency Cutoff completed.")
    return smoothed


#############UI############
root = tk.Tk()
root.resizable(False, False)
root.geometry("850x600")
root.title("Smooth Stock Data-HOANG ANH MINH-B23DCCN544-HVCNBCVT")

#Variables
start_date = tk.StringVar(root, "2022-08-09")
end_date = tk.StringVar(root, "2024-11-04")
stock_symbol = tk.StringVar(root, "FPT")
interval = tk.StringVar(root, "1D")

Using_amplitude_thresholding = tk.IntVar(root, 1)
Using_frequency_cutoff = tk.IntVar(root, 1)

using_custom_threshold = tk.IntVar(root, 0)
using_custom_cutoff_frequency = tk.IntVar(root, 0)

custom_threshold = tk.DoubleVar(root, 20000)
custom_cutoff_frequency = tk.DoubleVar(root, 0.01)

stock = stock_historical_data(stock_symbol.get(), start_date.get(), end_date.get(), interval.get(), 'stock')

#Graphs
fig = Figure(figsize=(10, 3.5))
graph = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()

# Guide
guide = tk.Label(master=root,text="-Date format: YYYY-MM-DD.\n-Interval:\n+1: 1 minutes           +30: 30 minutes\n+3: 3 minutes           +1H: 1 hour\n+5: 5 minutes           +1D: 1 day\n+15: 15 minutes\n*Notice 1: 1, 3, 5, 15, 30, 1H intervals can\nonly get data 90 days before the End date,\ncant go any further back. Only 1D interval\ncan go further than 90 days.\n*Notice 2: 1 min interval can be very slow due\nto ploting large amount of point using plot()\nso please wait about 30s if you use 1min\ninterval with long time frame.",font=("Times New Roman", 10), justify="left")
guide.pack(side=tk.LEFT)

# Settings of the graph
frame = tk.Frame(root)

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.columnconfigure(2, weight=1)
frame.columnconfigure(3, weight=1)

Amount_of_Data_Label = tk.Label(master=frame, text="Amount of point in graph:", font=("Times New Roman", 12))
Amount_of_Data_Label.grid(column=1, row=0, sticky="e")

Amount_of_Data = tk.Label(master=frame, text=str(len(stock)), font=("Times New Roman", 12))
Amount_of_Data.update()
Amount_of_Data.grid(column=2, row=0, sticky="w")

Amplitude_thresholding_Checkbutton = tk.Checkbutton(master=frame, text="Amplitude Thresholding",variable=Using_amplitude_thresholding, onvalue=1, offvalue=0,font=("Times New Roman", 11), fg="red")
Amplitude_thresholding_Checkbutton.grid(column=2, row=1)

Frequency_cutoff_Checkbutton = tk.Checkbutton(master=frame, text="Frequency Cutoff", variable=Using_frequency_cutoff,onvalue=1, offvalue=0, font=("Times New Roman", 11), fg="green")
Frequency_cutoff_Checkbutton.grid(column=0, row=1)

Start_date_Label = tk.Label(master=frame, text="Start date:", font=("Times New Roman", 12))
Start_date_Label.grid(column=0, row=2, sticky="w")

Start_date_Input = tk.Entry(master=frame, textvariable=start_date, width=15)
Start_date_Input.grid(column=1, row=2, sticky="w")

End_date_Label = tk.Label(master=frame, text="End date:", font=("Times New Roman", 12))
End_date_Label.grid(column=0, row=3, sticky="w")

End_date_Input = tk.Entry(master=frame, textvariable=end_date, width=15)
End_date_Input.grid(column=1, row=3, sticky="w")

Stock_symbol_Label = tk.Label(master=frame, text="Stock symbol:", font=("Times New Roman", 12))
Stock_symbol_Label.grid(column=2, row=2, sticky="w")

Stock_symbol_Input = tk.Entry(master=frame, textvariable=stock_symbol,width=7)
Stock_symbol_Input.grid(column=3, row=2,sticky="w")

Interval_Label = tk.Label(master=frame, text="Interval:", font=("Times New Roman", 12))
Interval_Label.grid(column=2, row=3, sticky="w")

Interval_Input = tk.Entry(master=frame, textvariable=interval, width=7)
Interval_Input.grid(column=3, row=3,sticky="w")

Custom_threshold_Checkbutton = tk.Checkbutton(master=frame, text="Using custom threshold", font=("Times New Roman", 12),
                                              variable=using_custom_threshold, onvalue=1, offvalue=0, fg="red")
Custom_threshold_Checkbutton.grid(column=1, row=4, sticky="w")

Custom_cutoff_frequency_Checkbutton = tk.Checkbutton(master=frame, text="Using custom cutoff frequency",font=("Times New Roman", 12),variable=using_custom_cutoff_frequency, onvalue=1, offvalue=0,fg="green")
Custom_cutoff_frequency_Checkbutton.grid(column=1, row=5, sticky="w")

Custom_threshold_Input = tk.Entry(master=frame, textvariable=custom_threshold, width=11)
Custom_threshold_Input.grid(column=2, row=4, sticky="w")

Custom_cutoff_frequency_Input = tk.Entry(master=frame, textvariable=custom_cutoff_frequency, width=11)
Custom_cutoff_frequency_Input.grid(column=2, row=5, sticky="w")

frame.pack()

confirm_button = tk.Button(master=root, text="Confirm changes", command=PlotSmoothedData, font=("Times New Roman", 12))
confirm_button.pack()

PlotSmoothedData()
root.mainloop()
