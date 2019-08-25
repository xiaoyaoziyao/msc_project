# How does the use of citations change over time?

Write code that is able to take the full-text of Citation Papers and identify the location of citations to Cited Papers and build a model that is able to predict the location of citations to Cited Papers based on the publication year of Citation Papers.

## Getting Started

The name and function of the files in this package is listed below.

1_doi_acquire.py - Acquire DOIs of citation papers - required files in WOS_list folder
2_xml_extract.py - Acquire XML files according to DOIs(every 10 cited papers as a unit and stored in a file) - xml files crawling (time-consuming)
3_location_extract.py - Extract the location - required database (connection.ncx imported into MongoDB)
4_data_visualize.py - Visualize the data by violin plot and swarm plot - required database (connection.ncx imported into MongoDB)
5_model_build.py - Build the prediction model - required database (connection.ncx imported into MongoDB) - default for classes
connection.ncx - MongoDB files
WOS_list folder - files downloaded from WoS, containing citation information.

### Prerequisites

Python 3.6
sklearn package
pymongo package
urllib package
pandas package
seaborn package
nltk package 
matplotlib package
imblearn package
numpy package

## Running

Run the code directly.

## Built With

* [Python](https://www.python.org/) 

## Authors

* **Zhiyao Qian** - *Initial work* - [Zhiyao Qian](https://github.com/xiaoyaoziyao/msc_project)
