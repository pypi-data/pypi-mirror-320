# Python Mempool API

Welcome to the **Python Mempool API** documentation!  Here, we take a wild ride through the world of Bitcoin using the [mempool.space](https://mempool.space/) REST API.  
Buckle up, because we're about to fetch some serious data!

## Introduction

Ever wanted to know the price of Bitcoin in your favorite currency? Or maybe check the balance of your Bitcoin address?  
Well, you've come to the right place!  
This Python package is your trusty sidekick in the quest for Bitcoin knowledge.  
For a full version of this document, check out the official [GitHub Repository](https://github.com/k0g1t0/python-mempool-api/tree/main).

## Notes

- **Supported FIAT Currencies**: for every method where a fiat currency is required, here is the list of the supported one
    - ***USD***
    - ***EUR***
    - ***GBP***
    - ***CAD***
    - ***CHF***
    - ***AUD***
    - ***JPY***

- **Time frames**: for every method where a timeframe is required here are the supported one `24h`, `3d`, `1w`, `1m`, `3m`, `6m`, `1y`, `2y`, `3y`

## How To Use

You can easily use and install this package by simply typing:

```
pip install python-mempool-api
```

1. **Import the desired class (the full list is available [here](https://github.com/k0g1t0/python-mempool-api/blob/main/README.md#classes))**

```
from mempool import <class>
```

2. **Create an object**

```
obj = <class()>
```

3. **Access the methods (the full list is available [here](https://github.com/k0g1t0/python-mempool-api/blob/main/README.md#methods))**

```
obj.<method>
```