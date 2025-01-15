from os.path import isdir, splitext
from json import load, dump
from os import mkdir

def check_dir( abs_path_to_directory, message = ' does not exist or is not a directory. Exiting. ' ):

      if not isdir( abs_path_to_directory ):

            msg = abs_path_to_directory + message
            raise IOError( msg )

def check_make_dir( abs_path_to_directory ):

	if not isdir( abs_path_to_directory ): mkdir( abs_path_to_directory )

def get_annot_file_name( image_file_name ):

	'''
	
		params
	
			image_file --> string representing an image file name, not absolute path

		return

			annot_file_name --> string representing the coresponding annotation file name
	'''

	name_, _ext = splitext( image_file_name )

	return name_ + '.json'

def get_mask_file_name( image_file_name ):

	'''
	
		params
	
			image_file --> string representing an image file name, not absolute path

		return

			annot_file_name --> string representing the coresponding annotation file name
	'''

	name_, _ext = splitext( image_file_name )

	return name_ + '.png'

def load_json( _file ):

	with open( _file, 'r' ) as fp:

		data = load( fp )

	return data

def dump_json( _file, data ):

	with open(_file, 'w') as fp:

		dump( data, fp, sort_keys = False, indent = 4, separators = (',', ': ') )

def split_list( to_split, percent ):

	'''

		params

			to_split --> python list ex: [ e1, e2, e3, ... ] 
			percent --> scalar in [0, 1]

		return

			list_ --> python list representing left slice
			_list --> pyhton list representing right slice
	'''

	#todo: check param validity

	num_examples = len( to_split )
	split_index = int( num_examples * percent )

	list_ = to_split[ :split_index ]
	_list = to_split[ split_index: ]

	return list_, _list
