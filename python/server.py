#!/usr/bin/python
from flask import Flask, request
import json
from flask_socketio import SocketIO
import numpy as np
import pygame
from weka.classifiers import Classifier, Evaluation, PredictionOutput
from weka.core.converters import Loader
import weka.core.jvm as jvm

app = Flask(__name__)
socketio = SocketIO(app)
pygame.mixer.init(44100, -16, 2, 1024)

# arrays to hold the data while it streams in
gyro_x = []
gyro_y = []
gyro_z = []
accel_x = []
accel_y = []
accel_z = []


def calculateFeatures(list):
    mean = np.mean(list)
    std = np.std(list)
    maxValue = np.max(list)
    minValue = np.min(list)
    iqr = np.subtract(*np.percentile(list, [75, 25]))
    return mean, std, maxValue, minValue, iqr


def getFeatures(xAcc, yAcc, zAcc, xGyr, yGyr, zGyr):
    retVal = []
    retVal += calculateFeatures(xAcc)
    retVal += calculateFeatures(yAcc)
    retVal += calculateFeatures(zAcc)
    retVal += calculateFeatures(xGyr)
    retVal += calculateFeatures(yGyr)
    retVal += calculateFeatures(zGyr)
    return retVal


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

    output.write(
        "@ATTRIBUTE class {upDown, leftRight, inOut, rotation}\n")
    output.write("@DATA\n")
    output.close


def processDataToArff(xAcc, yAcc, zAcc, xGyr, yGyr, zGyr):
    writeHeader('classify.arff')
    output = open('classify.arff', "a")
    features = getFeatures(xAcc, yAcc, zAcc, xGyr, yGyr, zGyr)
    for i in range(len(features)):
        output.write(str(features[i]))
        output.write(", ")
    output.write("?")
    output.write("\n")
    output.close()


def playD():
    pygame.mixer.music.load("./D.mid")
    pygame.mixer.music.play(loops=-1)


def playA():
    pygame.mixer.music.load("./A.mid")
    pygame.mixer.music.play(loops=-1)


def playBm():
    pygame.mixer.music.load("./Bm.mid")
    pygame.mixer.music.play(loops=-1)


def playG():
    pygame.mixer.music.load("./G.mid")
    pygame.mixer.music.play(loops=-1)


def stop():
    pygame.mixer.music.stop()


@socketio.on('message')
def handle_message(message):
    global accel_x
    global accel_y
    global accel_z
    global gyro_x
    global gyro_y
    global gyro_z
    if message['sensorName'] == 'accelerometer':
        accel_x.append(float(message['x']))
        accel_y.append(float(message['y']))
        accel_z.append(float(message['z']))
    elif message['sensorName'] == 'gyroscope':
        gyro_x.append(float(message['x']))
        gyro_y.append(float(message['y']))
        gyro_z.append(float(message['z']))
    elif message['sensorName'] == "stop":
        # stop signal
        stop()
    if len(gyro_x) >= 25 and len(accel_x) >= 25:
        # only classify when both gyroscope and accelerometer data has more than 25 samples
        processDataToArff(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        jvm.start()
        loader = Loader(classname="weka.core.converters.ArffLoader")
        # load the training data
        train = loader.load_file("train.arff")
        train.class_is_last()
        cls = Classifier(classname="weka.classifiers.trees.LMT")
        # train the classifier
        cls.build_classifier(train)
        pout = PredictionOutput(
            classname="weka.classifiers.evaluation.output.prediction.PlainText")
        evl = Evaluation(train)
        # load the classify data
        test = loader.load_file("classify.arff")
        test.class_is_last()
        evl.test_model(cls, test, pout)
        result = pout.buffer_content()
        resultLines = result.splitlines()
        for i in range(len(resultLines)):
            if (resultLines[i].find("upDown") != -1):
                result = 1
            elif (resultLines[i].find("leftRight") != -1):
                result = 2
            elif (resultLines[i].find("inOut") != -1):
                result = 3
            elif (resultLines[i].find("rotation") != -1):
                result = 4
            else:
                result = "error"
        if result == 1:
            stop()
            playD()
        elif result == 2:
            stop()
            playBm()
        elif result == 3:
            stop()
            playA()
        elif result == 4:
            stop()
            playG()
        # clear the arrays for new data
        gyro_x = []
        gyro_y = []
        gyro_z = []
        accel_x = []
        accel_y = []
        accel_z = []


if __name__ == "__main__":
    socketio.run(app)
