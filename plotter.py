from matplotlib import pyplot as plt
import pandas as pd
from image_to_bytes import img_bytes
import numpy as np



def response_time_chart(response_times, test_times):

    # courtesy: https://stackoverflow.com/questions/11280536/how-can-i-add-the-corresponding-elements-of-several-lists-of-numbers
    # add test time and response time for each click
    # example: reaction time is 10s and wait time is 8 s, then next plot bar should be add +18s on x-axis

    testsums = [sum(n) for n in zip(*[response_times, test_times])]
    
    # seconds to ms
    ms = np.multiply(response_times, 1000)

    # cumulate sum of each element in testsum list for plotting on x-axis
    resp = np.cumsum(testsums)

    #plot the bar
    
    fig, ax = plt.subplots()

    ax.bar(resp, ms)

    # set plot params: labels, font, and sizes
    ax.set_xlabel("Test Timeline (s)", fontsize = 15)
    ax.set_ylabel("Response Times (ms)", fontsize = 15)
    ax.set_title("Your Test Data Visualised", fontsize = 16)

    return img_bytes(plt)

