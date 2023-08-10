# Flight price predictor

After covid's outbreak in last few years we have seen a significant change in how flight price calculations change in time. Some sources even claim that some of the leading search engines have reduced the number of "predictive ingisghts" they used to provide to the users [source](https://www.wired.com/story/airfare-prediction-tools/). 

This project's goal is to create a model that gives a close prediction for a set amount of days in the future by first gathering flight prices data by scraping Google Flight's website.

## Overview of the project

Web scrapes Google Flight's website for the cheapest flight prices in the last 60 days for a list of flights, saves the information inside csv files, and feeds it to a Tensorflow model in order to make predictions about the prices in the future.

## Installation

To be able to run the application you need to have [Python3.10](https://www.python.org) and [pip](https://pypi.org/project/pip/) installed.
After installing them, simply run `./setup.sh` to install all the required dependencies.

## Usage

### Web scraper

Configure which cities you want to webscrape flights between inside webscrape_settings.yaml in flight_locations.
Choose the start_date and end_date that you want to webscrape between.
Finally, choose how many threads you want to be webscraping at the same time. 

**IMPORTANT**

**Choose this number according to your machine's capabilities.**

### Price predictor

In model trainer you can find visualization of the webscraped data. The data is later on min/max normalized in the range [0, 1] ignoring flights for which the price has not changed at all in the span of 60 days. 

Then a sliding window approach is used to preprocess the data. Since we have many flights with 60 data points per flight we decided to use a sliding window apporach in order to capture any trends that exist. *WINDOW_SIZE_X* specifies how many days we look back in the past and *WINDOW_SIZE_y* specifies how many days we are predicting for in the future. The data set is later on split into train and test with ratio 9:1 train to test.

The preprocessed data is then fed to a Tensorflow 2 model and subsequently trained. We use mean squared error for the loss function and [adam](https://www.google.com/search?client=safari&rls=en&q=adam+optimizer+tensorflow&ie=UTF-8&oe=UTF-8) for the optimizer. The decrease of the mean squared error can be observed in the next block. 

Finally, we predict *WINDOW_SIZE_y* in the future for few flights and see if the predicted prices make sense.

## License

[MIT](https://choosealicense.com/licenses/mit/)