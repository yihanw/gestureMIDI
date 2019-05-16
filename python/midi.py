#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 14:11:45 2019

@author: Jane
"""

from weka.classifiers import Classifier, Evaluation, PredictionOutput
from weka.core.converters import Loader
import numpy as np
import glob
import os
import weka.core.jvm as jvm
jvm.start()

"""
Training data: 
Fany: data1-10: upDown, data11-20: leftRight, data21-30: inOut, data31-40: rotation
Jane: jane1-10: leftRight, data11-20: upDown, data21-30: inOut, data31-40: rotation
LimJie: limjie1-10: upDown, limjie11-20: leftRight, limjie21-30: inOut, limjie31-40: rotation
"""

# process the raw data by splitting the numbers and converting them to float numbers
def processData(lines):
    xAcc = []
    yAcc = []
    zAcc = []
    xGyr = []
    yGyr = []
    zGyr = []
    for i in range(len(lines)):
        xAcc.append(float(lines[i].split(",")[0]))
        yAcc.append(float(lines[i].split(",")[1]))
        zAcc.append(float(lines[i].split(",")[2]))
        xGyr.append(float(lines[i].split(",")[3]))
        yGyr.append(float(lines[i].split(",")[4]))
        zGyr.append(float(lines[i].split(",")[5]))
    return xAcc, yAcc, zAcc, xGyr, yGyr, zGyr


# calculate features: mean, standard deviation, max, min and iqr
def calculateFeatures(list):
    mean = np.mean(list)
    std = np.std(list)
    maxValue = np.max(list)
    minValue = np.min(list)
    iqr = np.subtract(*np.percentile(list, [75, 25]))
    return mean, std, maxValue, minValue, iqr

# append the six features to an array
def getFeatures(xAcc, yAcc, zAcc, xGyr, yGyr, zGyr):
    retVal = []
    retVal += calculateFeatures(xAcc)
    retVal += calculateFeatures(yAcc)
    retVal += calculateFeatures(zAcc)
    retVal += calculateFeatures(xGyr)
    retVal += calculateFeatures(yGyr)
    retVal += calculateFeatures(zGyr)
    return retVal


# write header to arff file <filename>
def writeHeader(filename):
    output = open(filename, "w")
    output.write("@RELATION gesture\n")
    output.write("@ATTRIBUTE X_ACC_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE X_ACC_STD NUMERIC\n")
    output.write("@ATTRIBUTE X_ACC_MAX NUMERIC\n")
    output.write("@ATTRIBUTE X_ACC_MIN NUMERIC\n")
    output.write("@ATTRIBUTE X_ACC_IQR NUMERIC\n")

    output.write("@ATTRIBUTE Y_ACC_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE Y_ACC_STD NUMERIC\n")
    output.write("@ATTRIBUTE Y_ACC_MAX NUMERIC\n")
    output.write("@ATTRIBUTE Y_ACC_MIN NUMERIC\n")
    output.write("@ATTRIBUTE Y_ACC_IQR NUMERIC\n")

    output.write("@ATTRIBUTE Z_ACC_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE Z_ACC_STD NUMERIC\n")
    output.write("@ATTRIBUTE Z_ACC_MAX NUMERIC\n")
    output.write("@ATTRIBUTE Z_ACC_MIN NUMERIC\n")
    output.write("@ATTRIBUTE Z_ACC_IQR NUMERIC\n")

    output.write("@ATTRIBUTE X_GYR_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE X_GYR_STD NUMERIC\n")
    output.write("@ATTRIBUTE X_GYR_MAX NUMERIC\n")
    output.write("@ATTRIBUTE X_GYR_MIN NUMERIC\n")
    output.write("@ATTRIBUTE X_GYR_IQR NUMERIC\n")

    output.write("@ATTRIBUTE Y_GYR_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE Y_GYR_STD NUMERIC\n")
    output.write("@ATTRIBUTE Y_GYR_MAX NUMERIC\n")
    output.write("@ATTRIBUTE Y_GYR_MIN NUMERIC\n")
    output.write("@ATTRIBUTE Y_GYR_IQR NUMERIC\n")

    output.write("@ATTRIBUTE Z_GYR_MEAN NUMERIC\n")
    output.write("@ATTRIBUTE Z_GYR_STD NUMERIC\n")
    output.write("@ATTRIBUTE Z_GYR_MAX NUMERIC\n")
    output.write("@ATTRIBUTE Z_GYR_MIN NUMERIC\n")
    output.write("@ATTRIBUTE Z_GYR_IQR NUMERIC\n")

    output.write("@ATTRIBUTE class {upDown, leftRight, inOut, rotation}\n")
    output.write("@DATA\n") 
    output.close


# read in data from the train folder or the test foler, then calculate features and 
# output the features in arff format named as <filename>

def processDataToArff(filename, isTest):
    writeHeader(filename)
    output = open(filename, "a")

    if (isTest):
        path = "./test/"
    else:
        path = "./train/"

    for filename in glob.glob(os.path.join(path, '*.txt')):
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        label = lines[0]
        lines.pop(0)

        xAcc, yAcc, zAcc, xGyr, yGyr, zGyr = processData(lines)
        features = getFeatures(xAcc, yAcc, zAcc, xGyr, yGyr, zGyr)

        for i in range(len(features)):
            output.write(str(features[i]))
            output.write(", ")

        if (isTest):
            output.write("?")
        else:
            output.write(label)
        output.write("\n")

    output.close()


# output arff files
processDataToArff("train.arff", False)
processDataToArff("test.arff", True)


# setup training model
loader = Loader(classname="weka.core.converters.ArffLoader")
train = loader.load_file("train.arff")
train.class_is_last()
test = loader.load_file("test.arff")
test.class_is_last()
# print(train)

cls = Classifier(classname="weka.classifiers.trees.LMT") #use LMT as our algorithm
cls.build_classifier(train) #train the model using train.arff


pout = PredictionOutput(classname="weka.classifiers.evaluation.output.prediction.PlainText")
evl = Evaluation(train)
evl.test_model(cls, test, pout)

# print the result
result = pout.buffer_content()
#print(result)

# split the result and only print the gesture
resultLines = result.splitlines()
for i in range(len(resultLines)):
    if (resultLines[i].find("upDown") != -1):
        print("%d upDown" % (i+1))
    elif (resultLines[i].find("leftRight") != -1):
        print("%d leftRight" % (i+1))
    elif (resultLines[i].find("inOut") != -1):
        print("%d inOut" % (i+1))
    elif (resultLines[i].find("rotation") != -1):
        print("%d rotation" % (i+1))
    else:
        print("error")

jvm.stop()
