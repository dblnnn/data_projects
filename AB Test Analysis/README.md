# A/B Test Analysis 

This repository contains a project report for an A/B test analysis of website new feature. The analysis aims to determine whether the new feature should be implemented based on the results of the A/B test.

## Table of Contents

- [Introduction](#introduction)
- [Data Overview](#data-overview)
- [Key Findings](#key-findings)

## Introduction

The project is consists of two parts:
- ICE and RICE prioritization of features implementation
- Analysis of A/B test results for the new feature

The first part is a prioritization of features for implementation. After the prioritization, we will analyze the results of an A/B test for selected feature. The A/B test was conducted for a month. The test was conducted on 2 groups of users: control group and test group. The test group was shown the new feature, while the control group was shown the old version of the website. The goal of the test was to determine whether the new feature should be implemented based on the results of the A/B test.

## Data Overview

The data for the analysis is stored in the following files: 
- `hypothesis.csv` - contains the data for the ICE and RICE prioritization
- `orders.csv` - contains the data for the A/B test analysis
- `visitors.csv` - contains the data for the A/B test analysis

## Analysis Steps

The analysis is performed in the following steps:
- Data preprocessing
- ICE and RICE prioritization
- A/B test analysis
- Statistical significance test
- Filtering of outliers
- Statistical significance test for filtered data
- Conclusion

## Key Findings

Hypotheses tests showed that the new feature did have a statistically significant impact on the orders amount but not on the average order size. 

