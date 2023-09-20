# Bank Churn Analysis

This repo contains a project report for a churn analysis of a bank's customers. The analysis aims to determine portrait of a client who is likely to leave the bank as well as a retained client. 

## Table of Contents
- [Introduction](#introduction)
- [Data Overview](#data-overview)
- [Analysis Steps](#analysis-steps)
- [Key Findings](#key-findings)

## Introduction

The project is containing exploratory data analysis of a bank's customers followed by hypothesis testing and formulating recommendations for the bank's products team.
Data was prepared for the analysis by removing missing values and duplicates, changing data types, and adding new features.

## Data Overview

The data is stored in the `churn.csv` and contains the following columns:
 - `User ID` - unique identifier of a client
 - `score` is a credit score of a client
 - `city`
 - `gender`
 - `age`
 - `equity` - number representing total score of equities a client possesses
 - `balance` is a total balance on the client's accounts
 - `products` is a number of products that a client uses
 - `credit_card` is a binary feature that shows if a client uses a credit card
 - `last_activity` is a binary feature that shows if a client is active
 - `estimated_salary` is an estimated salary of a client
 - `churn` is a binary feature that shows if a client has left the bank

## Analysis Steps

The analysis is performed in the following steps:
 - Data preprocessing
 - Exploratory data analysis
 - Hypotheses testing
 - Conclusion
 - Recommendations

## Key Findings

2 Loyal client segments and 2 disloyal client segments were identified. Also a portrait of a client who is likely to leave the bank as well as a retained client was created. 
Some of recommendations for the bank's products team are:
 - Increase the number of products used by clients by promoting them
 - Promote credit cards to clients to engage them more in using the bank's services
 - Create a loyalty program for clients