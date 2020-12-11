# AMFinder - amfinder_model.py

import os
import sys

import keras
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import Dense
from keras.initializers import he_uniform

import amfinder_log as cLog
import amfinder_config as cConfig





def core_model(input_shape):
    """ This function builds the core models, i.e. the successive
      convolutions and maximum pooling, as well as the hidden dense
      layers. The output layer is left undefined and will be tuned
      to fit the annotation level (see functions below). """

    model = Sequential()

    # 126->124
    model.add(Conv2D(32, kernel_size=3, name='C11', input_shape=input_shape,
                     activation='relu', kernel_initializer=he_uniform()))

    # 124->122
    model.add(Conv2D(32, kernel_size=3, name='C12',
                     activation='relu', kernel_initializer=he_uniform()))

    # 122->120
    model.add(Conv2D(32, kernel_size=3, name='C13',
                     activation='relu', kernel_initializer=he_uniform()))

    # 120->60
    model.add(MaxPooling2D(pool_size=2, name='M1'))

    # 60->58
    model.add(Conv2D(64, kernel_size=3, name='C21',
                     activation='relu', kernel_initializer=he_uniform()))

    # 58->56
    model.add(Conv2D(64, kernel_size=3, name='C22',
                     activation='relu', kernel_initializer=he_uniform()))

    # 56->28
    model.add(MaxPooling2D(pool_size=2, name='M2'))

    # 28->26
    model.add(Conv2D(128, kernel_size=3, name='C31',
                     activation='relu', kernel_initializer=he_uniform()))

    # 26->24
    model.add(Conv2D(128, kernel_size=3, name='C32',
                     activation='relu', kernel_initializer=he_uniform()))

    # 24->12
    model.add(MaxPooling2D(pool_size=2, name='M3'))

    # 12->10
    model.add(Conv2D(128, kernel_size=3, name='C4',
                     activation='relu', kernel_initializer=he_uniform()))

    # 10->5
    model.add(MaxPooling2D(pool_size=2, name='M4'))

    model.add(Flatten(name='F'))

    model.add(Dense(64, activation='relu', name='FC1',
                    kernel_initializer=he_uniform()))

    model.add(Dropout(0.3, name='D1'))

    model.add(Dense(16, activation='relu', name='FC2',
                    kernel_initializer=he_uniform()))

    model.add(Dropout(0.2, name='D2'))

    return model



def root_segm(input_shape):
    """ This function returns a simple model for the less precise level
      of annotation, i.e. 'colonization', which has three mutually 
      exclusive categories: colonized, non-colonized, and background.
      As a result, the final layer uses categorical cross-entropy and
      softmax activation. """

    model = core_model(input_shape)

    model.add(Dense(3, activation='softmax', name='RS',
                  kernel_initializer=he_uniform()))

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['acc'])

    return model



def ir_struct(input_shape):
    """ This function returns a slightly more elaborate model for the
      intermediate level of annotation, i.e. 'arb_vesicles' which has
      four categories: arbuscules, vesicles, non-colonized roots, and
      background. As a result, the final layer uses binary
      cross-entropy and sigmoid activation. """

    model = core_model(input_shape)

    model.add(Dense(3, activation='sigmoid', name='IS',
                    kernel_initializer=he_uniform()))

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['acc'])

    return model



def get_input_shape(level):
    """ Retrieves the input shape corresponding to the given
        annotation level. """

    edge = cConfig.get('model_input_size')
    # Input images have red, green, and blue channels.
    return (edge, edge, 3)





def create():
    """ Returns a fresh model corresponding to the defined
        annotation level. """

    level = cConfig.get('level')
    input_shape = get_input_shape(level) 

    if level == 'RootSegm':

        return root_segm(input_shape)

    elif level == 'IRStruct':

        return ir_struct(input_shape)

    else:

        print('WARNING: Unknown annotation level {}'.format(level))
        return None



def pre_trained(path):
    """ Loads a pre-trained model and updates the annotation level
        according to its input shape. """

    model_name = os.path.basename(path)
    print(f'* Pre-trained model: {model_name}')
    
    # Loads model.
    model = keras.models.load_model(path)   
    dim = model.layers[0].input_shape
    
    x = dim[1] # tile width
    y = dim[2] # tile height
    z = dim[3] # number of annotation classes

    if x != y:
    
        cLog.error(f'Rectangular input shape ({x}x{y} pixels)',
                   exit_code=cLog.ERR_INVALID_MODEL_SHAPE)

    else:
    
        # Usual values are 62 pixels for colonization and arb_vesicles,
        # and 224 pixels for all_features.
        cConfig.set('model_input_size', x)

    if x == 62:

        cConfig.set('level', 'RootSegm')

    elif x == 126:

        cConfig.set('level', 'IRStruct')


    else:

        # Here we have no option but to raise an error and exit.
        # Pre-trained models must have a valid input shape.
        print(f'ERROR: Pre-trained model has {dim} dimensions.')
        sys.exit(INVALID_MODEL_SHAPE)

    return model



def load():
    """ Loads a pre-trained model, or creates a new one when the
        application runs in training mode. """

    path = cConfig.get('model')

    if cConfig.get('run_mode') == 'predict':

        if path is not None and os.path.isfile(path):

            return pre_trained(path)

        else:

            cLog.error('Please provide a pre-trained model',
                       exit_code=cLog.ERR_NO_PRETRAINED_MODEL)

    else:

        if path is not None and os.path.isfile(path):

            return pre_trained(path)

        else:

            print('* Creates an untrained model.')
            return create()
