from matplotlib import pyplot as plt
import pandas as pd
from image_to_bytes import img_bytes
import numpy as np


def age_sex_stats(df):
    
    # remove unknown sex and age groups
    df = df[ (df["age_group"] != "unknown") & (df["sex"] != "U")]
    
    # set order for age groups
    df["age_group"] = pd.Categorical(df["age_group"],
                                 categories=["0-4", "5-12", "13-15", "16-17", "17-21", 
                                             "22-25", "26-29", "30-39", "40-49",
                                             "50-59", "60-64", "64-69", "70+"], 
                                 ordered=True)
    
    # sort df by above defined order
    df.sort_values(["age_group"]).reset_index(inplace=True)
    
    # create the pivot plot
    # plt.figure(figsize = (16,9))
    df.pivot("age_group", "sex", "crashes").plot(kind='bar', width = 0.8)

    # set plot params: labels, font, and sizes
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)
    plt.xlabel("age group", fontsize = 15)
    plt.ylabel("no. of crashes", fontsize = 15)
    plt.suptitle("Accident stats by age and sex (5 kms radius)", fontsize = 18)

    return img_bytes(plt)



def tod_atm_stats(df):
    
    # remove rows where weather is unknown
    df = df[df["atm"] != "Not known"]

    # reset indices
    df.reset_index(inplace = True)
    df["tod"] = df["tod"].apply(lambda x: x / np.timedelta64(1, "h"))


    # x ticks -- every 4th element from data aggregated by 30 mins, ie plot tick for every 2nd hour
    x = [x for x in range(0,24,2)]   
        
    
    # create the pivot plot
    df.pivot("tod", "atm", "crashes").plot(kind = "line")

    # set plot params: labels, font, legend, and sizes
    plt.xticks(x, [str(x)+":00" for x in x], fontsize = 12, rotation="90")
    plt.yticks(fontsize = 12)
    plt.xlabel("Time of day", fontsize = 15)
    plt.ylabel("no. of crashes", fontsize = 15)
    plt.suptitle("Crashes: time of day and atmospheric condition", fontsize = 16)
    plt.legend(loc = "center right", ncol=1, 
               fancybox=True, shadow=True, 
               bbox_to_anchor=(1.4, 0.5),
               prop={'size': 12}
              )

    return img_bytes(plt)


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

    plt.bar(resp, ms)

    # set plot params: labels, font, and sizes
    plt.xlabel("Test Timeline (s)", fontsize = 15)
    plt.ylabel("Response Times (ms)", fontsize = 15)
    plt.suptitle("Your Test Data Visualised", fontsize = 16)

    return img_bytes(plt)

