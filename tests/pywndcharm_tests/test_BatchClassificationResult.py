#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2013 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#
#

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import re
import numpy as np

from os.path import sep, dirname, realpath
from tempfile import mkdtemp
from shutil import rmtree

pychrm_test_dir = dirname( realpath( __file__ ) ) #WNDCHARM_HOME/tests/pychrm_tests
wndchrm_test_dir = dirname( pychrm_test_dir ) + sep + 'wndchrm_tests'

from wndcharm.FeatureSet import FeatureSpace, FisherFeatureWeights,\
        DiscreteBatchClassificationResult, ContinuousFeatureWeights,\
        ContinuousBatchClassificationResult

class TestDiscreteBatchClassificationResult( unittest.TestCase ):
    """
    Test the classification functionality
    """
    
    def test_TiledFitOnFit( self ):
        """Uses a curated subset of the IICBU 2008 Lymphoma dataset, preprocessed as follows:
        auto-deconvolved, eosin channel only, tiled 5x6, 3 classes, 10 imgs per class,
        300 samples per class.
        """

        # Inflate the zipped test fit into a temp file
        import zipfile
        zipped_file_path = pychrm_test_dir + sep + 'lymphoma_t5x6_10imgseach.fit.zip'
        zf = zipfile.ZipFile( zipped_file_path, mode='r' )
        tempdir = mkdtemp()
        zf.extractall( tempdir )

        try:
            fitfilepath = tempdir + sep + zf.namelist()[0]
            #fs = FeatureSpace.NewFromFitFile( fitfilepath  )
            fs = FeatureSpace.NewFromFitFile( fitfilepath, tile_options=(5,6) )
            #fs.Print( verbose=True )
            #print "\n\n\n********************\n\n\n"
            #full_train, full_test = fs.Split( random_state=42, quiet=True )
            #full_train.Print( verbose=True )
            #full_test.Print( verbose=True )
            fs.Normalize( quiet=True )
            fw = FisherFeatureWeights.NewFromFeatureSpace( fs ).Threshold()
            reduced_fs = fs.FeatureReduce( fw.names )
            #reduced_test = full_test.FeatureReduce( fw.names )
            #reduced_test.Normalize( reduced_train, quiet=True )

            batch_result = DiscreteBatchClassificationResult.New( reduced_fs, reduced_fs, fw )
            #batch_result.Print()

        finally:
            rmtree( tempdir )

    def test_TiledTrainTestSplit( self ):
        """Uses a fake FeatureSpace"""

        from wndcharm.ArtificialFeatureSets import CreateArtificialFeatureSpace_Discrete
        fs_kwargs = {}
        fs_kwargs['name'] = "DiscreteArtificialFS 10-class"
        fs_kwargs['n_samples'] = 1000
        fs_kwargs['n_classes'] = 10 # 100 samples per class
        fs_kwargs['num_features_per_signal_type'] = 25
        fs_kwargs['initial_noise_sigma'] = 40
        fs_kwargs['noise_gradient'] = 20
        fs_kwargs['n_samples_per_group'] = 4 # 25 images, 2x2 tiling scheme
        fs_kwargs['interpolatable'] = True
        fs_kwargs['random_state'] = 43
        fs_kwargs['singularity'] = False
        fs_kwargs['clip'] = False

        fs = CreateArtificialFeatureSpace_Discrete( **fs_kwargs )

        train_set, test_set = fs.Split( random_state=False, quiet=True )
        train_set.Normalize( quiet=True )
        fw = FisherFeatureWeights.NewFromFeatureSpace( train_set ).Threshold()

        reduced_train_set = train_set.FeatureReduce( fw.names )
        reduced_test_set = test_set.FeatureReduce( fw.names )
        reduced_test_set.Normalize( reduced_train_set, quiet=True )

        batch_result = DiscreteBatchClassificationResult.New(
                reduced_train_set, reduced_test_set, fw  )
        batch_result.Print()
            

if __name__ == '__main__':
    unittest.main()
