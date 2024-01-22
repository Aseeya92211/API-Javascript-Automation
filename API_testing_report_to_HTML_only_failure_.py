#!/usr/bin/python
# -*- coding: utf-8 -*-
# import libraries
import os
os.system('pip3 install pandas')
os.system('pip3 install numpy')
os.system('pip3 install jinja2==3.0')
import pandas as pd
import numpy as np

# Creating a dataframe
df = pd.read_csv("NSDC_API_Testing_Report.csv")


# Creating a dataframe with required columns
df.drop(columns=['iteration',
                 'collectionName',
                 'url',
                 'code',
                 'responseSize',
                 'skipped'],axis=1)

# create new col as endpoint
df['EndPoint']=df["method"]+" "+ df["requestName"]


# Failed dataframe
df_fail = pd.DataFrame(df)
df_fail = df_fail[df_fail.failed.notnull()]

# Splitting multiple enteries on "executed"
try:
    df_fail["failed"] = df_fail["failed"].str.split(',')

except:
    pass

df_fail = df_fail.explode("failed").reset_index(drop=True)

# Adding a new status column and discard old one 
df_fail["Status"] = np.where(df_fail["failed"].notnull(), "FAIL", "PASS")

df_fail.drop(columns = ["requestName",
                  "method",
                  "status",
                  "executed"])

df_fail_validations = df_fail[["failed",
                 "EndPoint",
                 "Status",
                 "responseTime"]]

df_fail_validations.columns = ["Assertion Name",
                     "End Point",
                     "Status",
                     "Response Time in ms"]

# Index
#df_fail_validations += 1


# Successful Validations
df_pass = pd.DataFrame(df)
df_pass = df_pass[df_pass.executed.notnull()]

# Splitting multiple enteries on "executed"
try:
    df_pass["executed"] = df_pass["executed"].str.split(',')

except:
    pass

finally:
    df_pass = df_pass.explode("executed").reset_index(drop=True)

    # Adding a new status column and discard old one 
    df_pass["Status"] = np.where(df_pass["executed"].notnull(), "PASS", "FAIL")

    df_pass.drop(columns=["requestName",
                    "method",
                    "status",
                    "failed"])

    df_pass_validations = df_pass[["executed",
                "EndPoint",
                "Status",
                "responseTime"]]


    # Rename column name
    df_pass_validations.columns = ["Assertion Name",
                    "End Point",
                    "Status",
                    "Response Time in ms"]

    # Index
    #df_pass_validations += 1

    passed_count = df.query('status == "OK"').status.count()+df.query('status == "Created"').status.count()

    # DataFrame for Total Fail and Total Success Count
    data = {
        "Total Successful API's": [passed_count],
        "Total Successful Validations": [df_pass_validations['Status'].count()],
        "Total Failure API's": [len(df['status'])-passed_count],
        "Total Failure Validations": [df_fail_validations['Status'].count()]
    }
    df_stats = pd.DataFrame(data)

    # Write to an html file
    if data["Total Failure Validations"] == [0]:
        with open("API_Report.html", 'w') as file:
            file.write('<center>'
                        + '<h2><b> NSDC Dev Environment API Testing Report </b></h1><br><hr>'
                        + '<h3><b> Summary </b></h3>'
                        + df_stats.to_html(index=False, justify="center") + '<br><hr>'
                        + '</center>'
                        )
    else:
        with open("API_Report.html", 'w') as file:
            file.write('<center>'
                        + '<h2><b> NSDC Dev Environment API Testing Report </b></h1><br><hr>'
                        + '<h3><b> Summary </b></h3>'
                        + df_stats.to_html(index=False, justify="center") + '<br><hr>'
                        + '<h3><b><font color="red"> Failure Details </font> </b></h3>'
                        + df_fail_validations.to_html(index=False, justify="center") + '<br><hr>'
                        + '</center>'
                        )
