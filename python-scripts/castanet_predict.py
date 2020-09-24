# CastANet - castanet_predict.py

import os
import pyvips
import numpy as np
import pandas as pd

import castanet_log as cLog
import castanet_save as cSave
import castanet_model as cModel
import castanet_config as cConfig
import castanet_segmentation as cSegm
import castanet_activation_mapping as cMapping



def normalize(t):
    """ Simple normalization function. """

    return t / 255.0



def make_table(image, model):
    """ Predict mycorrhizal structures on a large image. 
        PARAMETERS
        image: pyvips.vimage.Image
            Large image (mosaic) from which tiles are extracted.
        model: Sequential (tensorflow).
            Model used to predict mycorrhizal structures.
    """

    edge = cConfig.get('tile_edge')
    nrows = image.height // edge
    ncols = image.width // edge

    # Creates the images to save the class activation maps.
    cMapping.initialize(nrows, ncols)

    if nrows == 0 or ncols == 0:

        return None

    else:

        bs = cConfig.get('batch_size')
        c_range = range(ncols)

        # Full row processing, from tile extraction to structure prediction.
        def process_row(r):
            # First, extract all tiles within a row.
            row = [cSegm.tile(image, r, c) for c in c_range]
            # Convert to NumPy array, and normalize.
            row = normalize(np.array(row, np.float32))
            # Predict mycorrhizal structures.
            prd = model.predict(row, batch_size=bs)
            # Retrieve class activation maps.
            cMapping.generate(model, row, r)
            # Update the progress bar.
            cLog.progress_bar(r + 1, nrows)
            # Return prediction as Pandas data frame.
            return pd.DataFrame(prd)

        # Initialize the progress bar.
        cLog.progress_bar(0, nrows)

        # Retrieve predictions for all rows within the image.
        results = [process_row(r) for r in range(nrows)]

        # Returns the class activation maps.
        cams = cMapping.retrieve()

        # Concat to a single Pandas dataframe and add header.
        table = pd.concat(results, ignore_index=True)
        table.columns = cConfig.get('header')

        # Add row and column indexes to the Pandas data frame.
        # col_values = 0, 1, ..., c, 0, ..., c, ..., 0, ..., c; c = ncols - 1
        col_values = list(range(ncols)) * nrows
        # row_values = 0, 0, ..., 0, 1, ..., 1, ..., r, ..., r; r = nrows - 1
        row_values = [x // ncols for x in range(nrows * ncols)]
        table.insert(0, column='col', value=col_values)
        table.insert(0, column='row', value=row_values)

        return (table, cams)



def run(input_images):
    """ For each image given as input, performs segmentation into tiles
        and predicts mycorrhizal structures. The final table is then
        saved as ZIP archive in the same location as the input image. """

    model = cModel.load()

    for path in input_images:
        base = os.path.basename(path)
        print(f'* Image {base}')
        image = pyvips.Image.new_from_file(path, access='random')
        table, cams = make_table(image, model)
        cSave.prediction_table(table, cams, path)
