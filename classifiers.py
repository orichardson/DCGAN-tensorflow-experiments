# -*- coding: utf-8 -*-
"""
Classifiers

Created on Fri Mar  2 05:18:46 2018

@author: Oliver
"""

import sys
import os
from sklearn import svm, metrics   
import numpy as np


def report(expected, predicted, classifier, message='') :
    creport = metrics.classification_report(expected, predicted)
    print("Classification report for classifier %s:\n%s\n" % (classifier, creport))
    print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted)) 
    
    with open('./record.txt', 'a') as log:
        log.writeline('\n' + ('*'*50) +'\n'+message+'\n\n'+ creport)
 
    return metrics.accuracy_score(expected, predicted)
    
def svc( dataset , logmessage=""):
    (x_train, y_train), (x_test, y_test) = dataset
    
    
    # turn the data in a (samples, feature) matrix:
    n_samples = len(y_train)
    x_train = x_train.reshape((n_samples, -1))
    
    # Create a classifier: a support vector classifier
    classifier = svm.SVC(gamma=0.001)
    
    # We learn the digits on the first half of the digits
    classifier.fit(x_train, y_train)
    
    # Now predict the value of the digit on the second half:
    expected = y_test
    predicted = classifier.predict(x_test)
    report(expected, predicted, classifier, logmessage)  


def net( dataset , logmessage="" ):
    import keras
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Flatten
    from keras.layers import Conv2D, MaxPooling2D
    from keras import backend as K

    (x_train, y_train), (x_test, y_test) = dataset
    
    batch_size = 128
    num_classes = 10
    epochs = 12
    # input image dimensions
    img_rows, img_cols = 28, 28    
    
    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
    
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
#    print('x_train shape:', x_train.shape)
#    print(x_train.shape[0], 'train samples')
#   print(x_test.shape[0], 'test samples')
    
    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=1,
              validation_data=(x_test, y_test))
     
    model.save('keras-mnist.model')
    y_pred = model.predict(x_test)
    report(y_test, y_pred, model, logmessage)
    
if __name__ == '__main__':
    import scipy.misc
    
    # Questions
    # HOw well trained on this test on original
    # train on this, test on thsi
    # train on original test on this.

    # trained on part this part original, test on original


    # samples are all in
    # /sampledir/fashion-n/split/...

    datasetname = sys.argv[1]
    # First load original dataset
    
    def getoriginaldata():
        if datasetname == 'fashion':
            from keras.datasets import fashion_mnist
            return fashion_mnist.load_data()
            
        elif datasetname == 'mnist':
            from keras.datasets import mnist
            return mnist.load_data()
                
    (xtrain, ytrain), (xtest, ytest) = getoriginaldata()
    X_stand = np.concatenate((xtrain, xtest), axis=0)
    Y_stand = np.concatenate((ytrain, ytest), axis=0)
    stand = (X_stand, Y_stand)
   
    
    Xs = []
    Ys = []
    
    datapath = './samples'
    folders = [f for f in os.listdir(datapath) if f.startswith(datasetname+'-')]
    
    for f in folders:
        label = int(f[len(datasetname)+1:])
        for imagename in os.listdir(datapath+'/'+f+'/split'):
            # VERY IMPORTANT. This next line makes sure shitty training things from 
            # early on in the GAN process are not reused.
            if ('test' in imagename):
                dataX = scipy.misc.imread(datapath+'/'+f+'/split/'+imagename)
                Xs.append(dataX)
                Ys.append(label)
            
    X_gen = np.array(Xs)
    Y_gen = np.array(Ys)
    gen = (X_gen, Y_gen)
    
    for model in [svc, net]:
        mstr = str(type(model))            
        model( (gen, stand) , mstr+" train on gen, test on standard for "+datasetname)
        model( (stand, gen), mstr+" train on stand, test on gen for "+datasetname)
        
        ntrain = int(0.7 * X_gen.shape[0])
        model( ((X_gen[:ntrain], Y_gen[:ntrain]), (X_gen[ntrain:], Y_gen[ntrain:])),
              mstr+" train on gen, test on gen for "+datasetname)

          
        
        
        
        

        
        
        
        
        
        
        
        