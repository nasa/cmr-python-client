#!/usr/bin/env python3

"""A simple test of the API from a command line script"""

import time

try:
    # Try loading the code from the python environment
    import cmr as cmr_imp
except ModuleNotFoundError:
    # Try to load the local system
    import os
    import sys
    sys.path.append(os.path.expanduser('.'))
    import cmr as cmr_imp
import cmr.search.collection as coll

# Terminal colors
def text_color(message='{}', color_code='\033[0;37m'):
    """Set text to a color, default color is White"""
    no_color = '\033[0m'
    return '{}{}{}'.format(color_code, message, no_color)

def red_text(msg='{}'):
    """Set text to red"""
    red_code = '\033[0;31m'
    return text_color(msg, red_code)

def green_text(msg='{}'):
    """Set text to green"""
    green_code = '\033[0;32m'
    return text_color(msg, green_code)

def blue_text(msg='{}'):
    """Set text to blue"""
    blue_code = '\033[0;34m'
    return text_color(msg, blue_code)

# Get to work
def main():
    """The commands main method"""
    print ("running version: {}".format(str(cmr_imp.BUILD)))
    print (blue_text("Enter in a free text search:"))
    ask = input(">")
    params = {}
    if len(ask)>0:
        params = {'keyword': ask}
    else:
        print ("No input given, use a default search")
        params = {'fake-parameter': 'value for fake parameter'}

    #params = {'polygon': '10,10,30,10,30,20,10,20,10,10'}
    print ('Searching for {}'.format(params))

    coll.set_logging_to('DEBUG')
    time_start = time.time()
    raw_results = coll.search(params, limit=5000, config={'env':'uat'})
    time_stop = time.time()

    durration = time_stop - time_start

    if 'errors' in raw_results:
        output_format = red_text('Error while searching: {}')
        output_result = raw_results['errors']
    else:
        filters = [coll.collection_core_fields,
            coll.drop_fields('EntryTitle'),
            coll.drop_fields('Version'),
            #coll.drop_fields('ShortName'),
            coll.drop_fields('concept-id')]
        output_format = green_text()
        output_result = coll.apply_filters(filters, raw_results)
        #output_result = raw_results

    for item in output_result:
        print (output_format.format(item))
    print ("It took {} seconds to pull {} records.".format(durration, len(raw_results)))

if __name__ == '__main__':
    main()
