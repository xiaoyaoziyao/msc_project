"""
Visualize the data by violin plot and swarm plot
"""
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sns
import pymongo


def visualize0():
    """
    Visualize 10 highly cited papers paper by paper
    after filtering the invalid data (citation_year>cited year && citation location is empty)
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    condition = {'$and': [{"cited_no": {'$lte': 10}},
                          {"location_no": {"$exists": True}},
                          {"location_no": {"$ne": None}},
                          {'$where': "this.citation_year > this.cited_year"}]}
    cursor = collection.find(condition)
    cited_nos = []
    year_diffs = []
    locations = []
    cited_years = []
    for docu in cursor:
        year_diff = docu["citation_year"] - docu["cited_year"]
        cited_no = docu["cited_no"]
        location = docu["stand_location"]
        cited_year = docu["cited_year"]
        for i in range(len(location)):
            year_diffs.append(year_diff)
            cited_nos.append(cited_no)
            cited_years.append(cited_year)
        for loc in location:
            locations.append(loc)
    no_year = list(zip(cited_nos, cited_years))
    sort_no_year = sorted(set(no_year))
    data = {'cited_no_year': cited_nos, 'citation_interval': year_diffs, 'location': locations}
    df = pd.DataFrame(data=data)
    fig = plt.figure(figsize=(16, 12), dpi=80)
    fig.add_subplot(211)
    sns.violinplot(x='cited_no_year', y='citation_interval', hue='location', inner='stick', data=df,
                   hue_order=["Others", "Introduction and Background",
                              "Materials and Methods", "Results and Discussion", "Conclusion"])
    plt.xticks(range(10), sort_no_year)
    # plt.tick_params(labelsize=16)
    # sns.boxplot(x='cited_no_year', y='citation_interval', hue='location', data=df,
    #                hue_order=["Others", "Introduction and Background",
    #                           "Materials and Methods", "Results and Discussion", "Conclusion"])
    fig.add_subplot(212)
    sns.swarmplot(x='cited_no_year', y='citation_interval', hue='location', data=df,
                  hue_order=["Others", "Introduction and Background",
                             "Materials and Methods", "Results and Discussion", "Conclusion"])
    plt.xticks(range(10), sort_no_year)
    # plt.tick_params(labelsize=16)
    plt.show()
    client.close()


def visualize1(a, b):
    """
    Visualize highly cited papers separately year by year during the citation interval
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']

    condition = {'$and': [{"cited_no": {'$gt': 20}},
                          {"cited_year": {'$gte': a, '$lt': b}},
                          {"location_no": {"$exists": True}},
                          {"location_no": {"$ne": None}},
                          {'$where': "this.citation_year >= this.cited_year"}]}
    cursor = collection.find(condition)
    cited_nos = []
    year_diffs = []
    locations = []
    cited_years= []
    for docu in cursor:
        year_diff = docu["citation_year"] - docu["cited_year"]
        cited_no = docu["cited_no"]
        location = docu["stand_location"]
        cited_year = docu["cited_year"]
        for i in range(len(location)):
            year_diffs.append(year_diff)
            cited_nos.append(cited_no)
            cited_years.append(cited_year)
        for loc in location:
            locations.append(loc)
    data = {'cited_year': cited_years, 'citation_interval': year_diffs, 'location': locations}
    df = pd.DataFrame(data=data)
    fig = plt.figure(figsize=(16, 12), dpi=80)
    ax1 = fig.add_subplot(211)
    sns.violinplot(x='cited_year', y='citation_interval', hue='location', inner='stick', data=df,
                   hue_order=["Others", "Introduction and Background", "Materials and Methods",
                              "Results and Discussion", "Conclusion"])
    # sns.boxplot(x='cited_year', y='citation_interval', hue='location', data=df,
    #             hue_order=["Others", "Introduction and Background",
    #                        "Materials and Methods", "Results and Discussion", "Conclusion"])
    # plt.tick_params(labelsize=16)
    ax2 = fig.add_subplot(212)
    sns.swarmplot(x='cited_year', y='citation_interval', hue='location', data=df,
                  hue_order=["Others", "Introduction and Background", "Materials and Methods",
                             "Results and Discussion", "Conclusion"])
    # plt.tick_params(labelsize=16)
    plt.show()
    client.close()


def visualize2():
    """
    Visualize highly cited papers group by citation interval of ten years in one graph
    """
    client = pymongo.MongoClient('localhost:27017', connect=True)
    db = client['msc_project']
    collection = db['citations']
    condition = {'$and': [{"cited_no": {'$gt': 20}},
                          {"cited_year": {'$gte': 1950, '$lt': 2019}},
                          {"location_no": {"$exists": True}},
                          {"location_no": {"$ne": None}},
                          {'$where': "this.citation_year >= this.cited_year"}]}
    cursor = collection.find(condition)
    cited_nos = []
    year_diffs = []
    locations = []
    cited_years = []
    for docu in cursor:
        year_diff = docu["citation_year"] - docu["cited_year"]
        cited_no = docu["cited_no"]
        location = docu["stand_location"]
        cited_year = docu["cited_year"]
        for i in range(len(location)):
            year_diffs.append(year_diff)
            cited_nos.append(cited_no)
            cited_years.append(cited_year)
        for loc in location:
            locations.append(loc)
    for i in range(len(cited_years)):
        if(cited_years[i] in range(1950,1960)):
            cited_years[i] = 1
        elif(cited_years[i] in range(1960,1970)):
            cited_years[i] = 2
        elif (cited_years[i] in range(1970,1980)):
            cited_years[i] = 3
        elif (cited_years[i] in range(1980,1990)):
            cited_years[i] = 4
        elif (cited_years[i] in range(1990,2000)):
            cited_years[i] = 5
        elif (cited_years[i] in range(2000,2006)):
            cited_years[i] = 6
        elif (cited_years[i] in range(2006,2019)):
            cited_years[i] = 7
    # print(len(cited_years), len(year_diffs))
    data = {'cited_period': cited_years, 'citation_interval': year_diffs, 'location': locations}
    df = pd.DataFrame(data=data)
    fig = plt.figure(figsize=(16, 12), dpi=80)
    ax1 = fig.add_subplot(211)
    sns.violinplot(x='cited_period', y='citation_interval', hue='location', inner='stick', data=df,
                   hue_order=["Others", "Introduction and Background", "Materials and Methods",
                              "Results and Discussion", "Conclusion"])
    # sns.boxplot(x='cited_period', y='citation_interval', hue='location', data=df,
    #             hue_order=["Others", "Introduction and Background",
    #                        "Materials and Methods", "Results and Discussion", "Conclusion"])
    ax1.set_xticklabels(("1950-1959", "1960-1969", "1970-1979", "1980-1989", "1990-1999", "2000-2005", "2006-2016"))
    # plt.tick_params(labelsize=16)
    fig.add_subplot(212)
    sns.swarmplot(x='cited_period', y='citation_interval', hue='location', data=df,
                  hue_order=["Others", "Introduction and Background", "Materials and Methods",
                             "Results and Discussion", "Conclusion"], dodge=True)
    # plt.tick_params(labelsize=16)
    plt.show()
    client.close()


"""
Main function
"""
visualize0()
visualize1(1950,1979)
visualize1(1980,1989)
visualize1(1990,2005)
visualize1(2006,2019)
visualize2()
