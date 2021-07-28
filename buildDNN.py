from newFunctions import *

savePlot = False
NN = 'DNN'
useWeights = True
cutTrainEvents = False
print(Fore.BLUE + '         useWeights = ' + str(useWeights))
print(Fore.BLUE + '     cutTrainEvents = ' + str(cutTrainEvents))

### Reading the command line
jetCollection, analysis, channel, preselectionCuts, background, trainingFraction, signal, numberOfNodes, numberOfLayers, numberOfEpochs, validationFraction, dropout, testMass = ReadArgParser()

### Reading the configuration file
dfPath, InputFeatures = ReadConfig(analysis, jetCollection) 
dfPath += analysis + '/' + channel + '/' + str(signal) + '/' + background

### Loading input data
data_train, data_test, X_train_unscaled, m_train_unscaled, m_test_unscaled = LoadData(dfPath, jetCollection, str(signal), analysis, channel, background, trainingFraction, preselectionCuts, InputFeatures) 

### Removing 'mass' from the list of variables that will be given as input to the DNN
InputFeatures.remove('mass')

originsBkgTest = list(background.split('_')) ### in readarg? 

### Building the DNN
model = BuildDNN(len(InputFeatures), numberOfNodes, numberOfLayers, dropout)

### Dividing signal from background
data_test_signal = data_test[data_test['isSignal'] == 1]
data_test_bkg = data_test[data_test['isSignal'] == 0]
m_test_unscaled_signal = m_test_unscaled[data_test['isSignal'] == 1]
data_train_signal = data_train[data_train['isSignal'] == 1]
data_train_bkg = data_train[data_train['isSignal'] == 0]
m_train_unscaled_signal = m_train_unscaled[data_train['isSignal'] == 1]

### Saving unscaled train signal masses
unscaledTrainMassPointsList = list(dict.fromkeys(list(m_train_unscaled_signal)))

### Extracting scaled test/train signal masses
m_test_signal = data_test_signal['mass']
m_train_signal = data_train_signal['mass']
scaledTrainMassPointsList = list(dict.fromkeys(list(m_train_signal)))

if testMass == ['all']:
    testMass = [] ############################ serve?
    testMass = list(str(int(item)) for item in set(list(m_test_unscaled_signal)))

foundTestMass = 0
for mass in scaledTrainMassPointsList:

    ### Associating the scaled mass to the unscaled one
    unscaledMass = unscaledTrainMassPointsList[scaledTrainMassPointsList.index(mass)]

    ### Selecting only the request signal
    if str(int(unscaledMass)) not in testMass:
        continue
    foundTestMass += 1

    ### Creating the output directory
    outputDir = dfPath + '/' + NN + '/useWeights' + str(useWeights) + '/cutTrainEvents' + str(cutTrainEvents) + '/' + str(int(unscaledMass))
    print (format('Output directory: ' + Fore.GREEN + outputDir), checkCreateDir(outputDir))

    ### Creating the logFile
    logFileName = outputDir + '/logFile.txt'
    logFile = open(logFileName, 'w')
    logFile.write('dfPath: ' + dfPath + '\nNumber of train events: ' + str(len(data_train)) + ' (' + str(len(data_train_signal)) + ' signal and ' + str(len(data_train_bkg)) + ' background)' + '\nNumber of test events: ' + str(len(data_test)) + ' (' + str(len(data_test_signal)) + ' signal and ' + str(len(data_test_bkg)) + ' background)' + '\nInputFeatures: ' + str(InputFeatures) + '\nNumber of nodes: ' + str(numberOfNodes) + '\nNumber of layers: ' + str(numberOfLayers) + '\nNumber of epochs: ' + str(numberOfEpochs) + '\nValidation fraction: ' + str(validationFraction) + '\nDropout: ' + str(dropout) + '\nuseWeights: ' + str(useWeights))

    ### Selecting signal events with the same mass
    data_train_signal_mass = data_train_signal[data_train_signal['mass'] == mass]
    data_test_signal_mass = data_test_signal[data_test_signal['mass'] == mass]
    logFile.write('\nNumber of train signal events with mass ' + str(unscaledMass) + ': ' + str(len(data_train_signal_mass)) + '\nNumber of test signal events with mass ' + str(unscaledMass) + ': ' + str(len(data_test_signal_mass)))

    ### Putting signal and background events back together
    data_train_mass = pd.concat([data_train_signal_mass, data_train_bkg], ignore_index = True)
    data_test_mass = pd.concat([data_test_signal_mass, data_test_bkg], ignore_index = True)

    ### Shuffling data
    data_train_mass = ShufflingData(data_train_mass)
    data_test_mass = ShufflingData(data_test_mass)

    ### Extracting y_mass and origin_mass as numpy arrays
    y_train_mass = np.asarray(data_train_mass['isSignal'].values).astype(np.float32)
    y_test_mass = np.asarray(data_test_mass['isSignal'].values).astype(np.float32)
    origin_train_mass = np.array(data_train_mass['origin'].values)
    origin_test_mass = np.array(data_test_mass['origin'].values)

    ### Selecting only the variables to give to the DNN
    X_train_mass = data_train_mass[InputFeatures]
    X_test_mass = data_test_mass[InputFeatures]

    ### Converting pandas dataframes into numpy arrays
    X_train_mass = np.asarray(X_train_mass.values).astype(np.float32)
    X_test_mass = np.asarray(X_test_mass.values).astype(np.float32)

    '''
    if cutTrainEvents == True:
        #data_train_mass, y_train_mass = cutEvents(data_train_mass, y_train_mass)
        data_train_mass, y_train_mass, origin_train_bkg_mass = cutEventsNew(data_train_mass, origin_train_mass)
        data_train_bkg = data_train_mass[y_train_mass == 0]
    logFile.write('\nNumber of real train events with this mass (without validation set): ' + str(data_train_mass.shape[0]) + ' (' + str(sum(y_train_mass)) + ' signal and ' + str(len(y_train_mass) - sum(y_train_mass)) + ' background, Zjets: ' + str(list(origin_train_mass).count(1)) + ' and ' + str(list(origin_train_mass).count(2)) + ' Diboson)') ### origin_train_bkg_mass
    '''

    ### Weighting train events
    w_train_mass = None
    if(useWeights == True):
        #logFile.write('\nWeight for train signal events: ' + str(w_train_signal) + ', for background train events: ' + str(w_train_bkg))
        w_train_mass = weightEvents(origin_train_mass)

    ### Compiling and training
    callbacks = [
        # If we don't have a decrease of the loss for 11 epochs, terminate training.
        EarlyStopping(verbose = False, patience = 10, monitor = 'val_loss')
    ]
    model.compile(loss = 'binary_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])

    modelMetricsHistory = model.fit(X_train_mass, y_train_mass, sample_weight = w_train_mass, epochs = numberOfEpochs, batch_size = 2048, validation_split = validationFraction, verbose = 0, callbacks = callbacks)

    ### Saving to files
    ##SaveModel(model, data_train_unscaled, InputFeatures, outputDir)
    #model.save(outputDir + '/model/') ### per Martino

    ### Evaluating the performance of the DNN
    testLoss, testAccuracy = EvaluatePerformance(model, X_test_mass, y_test_mass)
    
    logFile.write('\nTest Loss: ' + str(testLoss) + '\nTest Accuracy: ' + str(testAccuracy))
    if savePlot:
        DrawLoss(modelMetricsHistory, testLoss, outputDir, NN, jetCollection, analysis, channel, preselectionCuts, signal, background, useWeights, cutTrainEvents, unscaledMass)
        DrawAccuracy(modelMetricsHistory, testAccuracy, outputDir, NN, jetCollection, analysis, channel, preselectionCuts, signal, background, useWeights, cutTrainEvents, unscaledMass)

    ### Prediction on the whole test sample and confusion matrix
    yhat_test = model.predict(X_test_mass, batch_size = 2048) 
    if savePlot:
        DrawCM(yhat_test, y_test_mass, True, outputDir, unscaledMass, background)

    ### Prediction on signal and background separately 
    X_train_signal_mass = X_train_mass[y_train_mass == 1]
    X_test_signal_mass = X_test_mass[y_test_mass == 1]
    X_train_bkg = X_train_mass[y_train_mass == 0]
    X_test_bkg = X_test_mass[y_test_mass == 0]
    yhat_train_signal, yhat_train_bkg, yhat_test_signal, yhat_test_bkg = PredictionSigBkg(model, X_train_signal_mass, X_train_bkg, X_test_signal_mass, X_test_bkg)

    ### Drawing scores, ROC and background rejection
    AUC, WP, WP_rej = DrawEfficiency(yhat_train_signal, yhat_test_signal, yhat_train_bkg, yhat_test_bkg, outputDir, NN, unscaledMass, jetCollection, analysis, channel, preselectionCuts, signal, background, savePlot, useWeights, cutTrainEvents)
    print(Fore.BLUE + 'AUC: ' + str(AUC))
    logFile.write('\nAUC: ' + str(AUC) + '\nWorking points: ' + str(WP) + '\nBackground rejection at each working point: ' + str(WP_rej))

    with open(outputDir + '/BkgRejection_' + background + '_last.txt', 'a') as BkgRejectionFile:
        BkgRejectionFile.write(str(WP_rej[0]) + '\n')
    '''
    np.savetxt('data_test_mass.csv', data_test_mass, delimiter = ',', fmt = '%s')
    np.savetxt('y_test_mass.csv', y_test_mass, delimiter = ',', fmt = '%s')

    scoresFile = open(outputDir + '/Scores.txt', 'w')
    for score in yhat_test:
        scoresFile.write(str(score) + '\n')
    scoresFile.close()
    '''

    ### Dividing sample by origin
    if len(originsBkgTest) > 1:
        for origin in originsBkgTest:
            logFile.write('\nOrigin: ' + origin)
            originsTest = origin_test_mass.copy()

            ### Selecting events with origin equal to signal or the background considered
            originsTest = np.where(originsTest == signal, 1, originsTest)
            originsTest = np.where(originsTest == origin, 1, originsTest)
            X_test_mass_origin = X_test_mass[originsTest == 1]
            y_test_mass_origin = y_test_mass[originsTest == 1]

            ### Prediction on the whole test sample and confusion matrix
            yhat_test_origin = model.predict(X_test_mass_origin, batch_size = 2048) 
            if savePlot:
                DrawCM(yhat_test_origin, y_test_mass_origin, True, outputDir, unscaledMass, background)

            ### Prediction on signal and background separately
            X_train_bkg_origin = X_train_mass[origin_train_mass == origin]
            X_test_bkg_origin = X_test_mass[origin_test_mass == origin]
            logFile.write('\nNumber of background train events with origin ' + origin + ': ' + str(len(X_train_bkg_origin)) + '\nNumber of background test events with origin ' + origin + ': ' + str(len(X_test_bkg_origin)))
            logFile.write('\nNumber of test events with origin ' + origin + ': ' + str(len(X_test_mass_origin)))
            yhat_train_signal_origin, yhat_train_bkg_origin, yhat_test_signal_origin, yhat_test_bkg_origin = PredictionSigBkg(model, X_train_signal_mass, X_train_bkg_origin, X_test_signal_mass, X_test_bkg_origin) ### quelle sul segnale non sono cambiate!

            ### Drawing scores, ROC and background rejection
            AUC, WP, WP_rej = DrawEfficiency(yhat_train_signal_origin, yhat_test_signal_origin, yhat_train_bkg_origin, yhat_test_bkg_origin, outputDir, NN, unscaledMass, jetCollection, analysis, channel, preselectionCuts, signal, background, savePlot, useWeights, cutTrainEvents)
            print(Fore.BLUE + 'AUC: ' + str(AUC))
            logFile.write('\nAUC: ' + str(AUC) + '\nWorking points: ' + str(WP) + '\nBackground rejection at each working point: ' + str(WP_rej))

            '''
            np.savetxt('data_train_signal_mass.csv', data_train_signal_mass, delimiter = ',', fmt = '%s')
            np.savetxt('data_train_bkg.csv', data_train_bkg, delimiter = ',', fmt = '%s')

            np.savetxt('data_test_signal_mass.csv', data_test_signal_mass, delimiter = ',', fmt = '%s')
            np.savetxt('data_test_bkg.csv', data_test_bkg, delimiter = ',', fmt = '%s')
            '''

            with open(outputDir + '/BkgRejection_' + origin + '_last.txt', 'a') as BkgRejectionFile:
                BkgRejectionFile.write(str(WP_rej[0]) + '\n')

    ### Closing the logFile
    logFile.close()
    print('Saved ' + logFileName)
    
if foundTestMass == 0:
    print(Fore.RED + 'No signal in the sample has the selected mass')
