#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
''' Initialize with default environment variables '''
__name__ = "scraperUtils"
__package__ = "scraper"
__module__ = "ota"
__app__ = "wrangler"
__conf_fname__ = "app.ini"

''' Load necessary and sufficient python librairies that are used throughout the class'''
try:
    ''' standard python packages '''
    import os
    import sys
    import logging
    import traceback
    import configparser
    import pandas as pd
    from datetime import datetime, date, timedelta, timezone

    print("All {0} in {1} software packages loaded successfully!"\
          .format(__package__,__module__))

except Exception as e:
    print("Some software packages in {0} didn't load\n{1}".format(__package__,e))


'''
    CLASS spefic to providing reusable functions for scraping ota data
'''

class Utils():

    ''' Function
            name: __init__
            parameters:

            procedure: Initialize the class
            return None

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def __init__(self, desc : str="OTA Utilities Class", **kwargs):

        self.__name__ = __name__
        self.__package__ = __package__
        self.__module__ = __module__
        self.__app__ = __app__
        self.__conf_fname__ = __conf_fname__
        if desc is None:
            self.__desc__ = " ".join([self.__app__,
                                      self.__module__,
                                      self.__package__,
                                      self.__name__])
        else:
            self.__desc__ = desc
        self._scrapeInterval=60   # set the scrape interval to 30 seconds

        global config
        global logger
#         global dataio
        global clsFile

        self.cwd=os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(os.path.join(self.cwd,__conf_fname__))

        self.rezHome = config.get("CWDS","REZAWARE")
        sys.path.insert(1,self.rezHome)
        ''' innitialize the logger '''
        from rezaware import Logger as logs
        logger = logs.get_logger(
            cwd=self.rezHome,
            app=self.__app__, 
            module=self.__module__,
            package=self.__package__,
            ini_file=self.__conf_fname__)

        ''' set a new logger section '''
        logger.info('########################################################')
        logger.info(self.__name__)
#         logger.info('Module Path = %s', self.pckgDir)
        ''' initialize file read/write '''
        from utils.modules.etl.load import sparkFILEwls as spark
        clsFile = spark.FileWorkLoads(desc="ota property price scraper")
        clsFile.storeMode=config.get("DATASTORE","MODE")
        clsFile.storeRoot=config.get("DATASTORE","ROOT")
        
        ''' UNUSED import dataio utils to read and write data '''
#         from utils.modules.etl.load import filesRW as rw
#         clsRW = rw.FileWorkLoads(desc=self.__desc__)
#         clsRW.storeMode = config.get("DATASTORE","MODE")
#         clsRW.storeRoot = config.get("DATASTORE","ROOT")
        self.storePath = os.path.join(
#             self.cwd,
            self.__app__,
            "data/",
            self.__module__,
            self.__package__,
        )

        self.scrape_start_date = date.today()
        self.scrape_end_date = self.scrape_start_date + timedelta(days=1)
        self.scrapeTimeGap = 30


        print("Initialing %s class for %s with instance %s" 
              % (self.__package__, self.__name__, self.__desc__))
        return None

    ''' Function
            name: get_url_list
            parameters:
                dirPath - the relative or direct path to the file with urls
                fileName - the name of the file containing all the urls for scraping
            procedure: read the list of urls from the CSV file and compile a list
            return list (url_list)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
#     def load_ota_list(self, file_path:str, **kwargs) -> dict:
    def load_ota_list(
        self,
        folder_path:str=None,
        file_name:str=None,
        **kwargs) -> dict:

        import os         # apply directory read functions
        import csv        # to read the csv
        import json       # to read the json file

        _s_fn_id = "function <load_ota_list>"
#         logger.debug("Executing %s %s" % (self.__name__, _s_fn_id))

        _ota_dict = {}
        
        try:

            ''' Get the list of urls from the CSV file '''        
#             if not file_path:
#                 raise ValueError("Invalid file path to load the ota list of inputs")

            ''' read the list of urls from the file '''
#             with open(file_path, newline='') as f:
#                 _ota_dict = json.load(f)
            _ota_dict = clsFile.read_files_to_dtype(
                as_type='dict',
                folder_path=folder_path,
                file_name=file_name,#__local_file_name__,
                file_type=None,
                **kwargs,
            )
            if len(_ota_dict) <=0:
                raise ValueError("Empty dictionary, NO destination data recovered from %s in %s"
                                 %(folder_path,file_name))
            logger.info("%s %s loaded %d OTA lists from %s in %s",
                        self.__name__, _s_fn_id,len(_ota_dict),file_name,folder_path)

        except Exception as err:
            logger.error("%s %s",__s_fn_id__, err)
            logger.debug(traceback.format_exc())
            print("[Error]"+__s_fn_id__, err)

        return _ota_dict

    ''' Function
            name: get_scrape_input_params
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)
            
            author: <nuwan.waidyanatha@rezgateway.com>

            TODO - change the ota_scrape_tags_df to a list of dictionaries
    '''
    def get_scrape_input_params(self, inputs_dict:dict):

        _s_fn_id = "function <get_scrape_input_params>"

        try:
            ''' check for property dictionary '''
            if not inputs_dict:
                raise ValueError("Invalid dictionary")

            ''' loop through the dict to construct the scraper parameters '''
            ota_param_list = []
            _l_tag=[]
            for input_detail in inputs_dict:
                param_dict = {}
                tag_dict = {}
                ''' create a dict with input params '''
                param_dict['ota'] = input_detail
                for detail in inputs_dict[input_detail]:
                    param_dict['url'] = detail['url']
                    param_dict['inputs'] = detail['inputs']
                    param_dict['locations'] = detail['locations']
                    ''' append the input parameters into a list'''
                    ota_param_list.append(param_dict)
      
            if len(ota_param_list)<=0:
                raise ValueError("No input parameter lists constructed")
            logger.info("%s %s constructed %d parameter lists",
                        self.__name__, _s_fn_id,len(ota_param_list))

        except Exception as err:
            logger.error("%s %s",__s_fn_id__, err)
            logger.debug(traceback.format_exc())
            print("[Error]"+__s_fn_id__, err)

        return ota_param_list #, ota_scrape_tags_df

    ''' Function -- TODO --
            name: get_scrape_output_params
            parameters:
                airline_dict - obtained from loading the property scraping parameters from the JSON

            procedure: loop through the loaded dictionary to retrieve the output variable names, tags, and values.
                        Then construcct and return a dataframe for all corresponding OTAs
            return dataframe (_scrape_tags_df)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def get_scrape_html_tags(self, airline_dict:dict):

        _scrape_tags_df = pd.DataFrame()

        _s_fn_id = "function <get_scrape_output_params>"
        logger.info("Executing %s %s" % (self.__package__, _s_fn_id))

        try:
            if not airline_dict:
                raise ValueError("Invalid properties dictionary")

            ''' loop through the dict to construct html tags to retrieve the data elements '''
            for input_detail in airline_dict:
                for _prop_params in airline_dict[input_detail]:
                    for _out_vars in _prop_params['outputs']:
                        _out_vars['ota'] = input_detail
                        _scrape_tags_df = pd.concat([_scrape_tags_df,\
                                                     pd.DataFrame([_out_vars.values()], columns=_out_vars.keys())],
                                                   ignore_index=False)

        except Exception as err:
            logger.error("%s %s \n", _s_fn_id,err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _scrape_tags_df

    ''' Function
            name: insert_params_in_url
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def insert_params_in_url(self, url: str, **kwargs ):

        import re

        url_w_params = None

        _s_fn_id = "function <insert_params_in_url>"
#        logger.info("Executing %s %s" % (self.__package__, _s_fn_id))

        try:
            if not url:
                raise ValueError("Invalid url string %s" % (url))
            url_w_params = url

            ''' match the keys in dict with the placeholder string in the url''' 
            for key in kwargs.keys():
                _s_regex = r"{"+key+"}"
                urlRegex = re.compile(_s_regex, re.IGNORECASE)
                param = urlRegex.search(url_w_params)
                if param:
                    _s_repl_val = str(kwargs[key]).replace(" ","%20")
                    url_w_params = re.sub(_s_regex, _s_repl_val, url_w_params)
            
        except Exception as err:
            logger.error("%s %s \n", _s_fn_id, err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return url_w_params

    ''' Function --- GET TIMESTAMPed STORAGE PATH ---

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def get_timestamped_storage(
        self,
        folder_path:str=None,   # folder path relative to the root dir or bucket
        folder_prefix:str="",   # a prefix to append to the begining of the time stamp
        folder_postfix:str="",  # a postfix to append to the end of the time stamp
        timestamp:datetime=datetime,  # the timestamp to extract the yyyy-mm-dd
        minute_interval:int=0,   # hh:mm will be rounded up or down to the interval
        **kwargs,
    ) -> str:
        """
        Description:
            The scraping is performed at a pertimcular time or with the interest of
            acquring data for a particular time period. The data will be organized in
            chronological order. To that end, the data should be stored in a folder
            with a timestamp as a postfix. The function will:
            * Use the imput timestamp and the scraping frequency to create a folder name
            * If the folder in the given path does not exist, it will create the folder
                * local file systems need the folder create before storing data
                * AWS S3 & GDS do not require folder to be created
            * Make use of utils/etl/loader/sparkFILEwls to manage this process
        Attributes:
            folder_path (str) - folder path relative to the root dir or bucket
            folder_prefix (str) -a prefix to append to the time stamp
            timestamp (datetime)- the timestamp to extract the yyyy-mm-dd
            minute_interval (int) - hh:mm will be rounded up or down to the interval
            **kwargs,
        Returns:
            rel_dir_path_ (str) returns a relative directory path with new folder
        Exceptions:
            * sparkFILEwls to validate and set the folder_path; if not exists
            * sparkFILEwls to validate and set the folder_path joined folder; if not exists
            * timestamp is None, will default to current datetime
            * minute_interval is not specified, will default to 0; i.e. every hour
        """
        
        __s_fn_id__ = "function <get_timestamped_storage>"

        rel_dir_path_ = None
        
        try:
            ''' validate folder path to set new folder '''
            clsFile.folderPath = folder_path
            ''' create the new folder with concaternating date hour and minute;
                rounding to the closest minute specified in the minute_interval'''
            if not isinstance(minute_interval,int):
                minute_interval=self._scrapeInterval
            if minute_interval < 0 or minute_interval > 60:
                logger.warning("Converting %d to int between 0 and 60: %d",
                               minute_interval,(abs(minute_interval)%60))
                minute_interval=abs(minute_interval) % 60
            if not isinstance(timestamp,datetime):
                timestamp=datetime.now()
                logger.warning("Invalid timestamp dtype; setting to default current datetime %s",
                               str(timestamp))
            if minute_interval != 0:
                _scrape_dt = timestamp + (datetime.min - timestamp) % timedelta(minutes=minute_interval)
            else:
                _scrape_dt = timestamp + ((datetime.min - timestamp) % timedelta(minutes=60)) \
                                    - timedelta(minutes=60)
            ''' create the timestamped folder name '''
            _dt_dir_name = "-".join([folder_prefix,str(_scrape_dt.year),str(_scrape_dt.month),
                                     str(_scrape_dt.day),str(_scrape_dt.hour),
                                     str(_scrape_dt.minute),folder_postfix])
            _dt_dir_name=_dt_dir_name.rstrip('-').lstrip('-')
            rel_dir_path_ = os.path.join(clsFile.folderPath, _dt_dir_name)
            clsFile.folderPath=rel_dir_path_
            logger.debug("Folder %s created in directory path %s",_dt_dir_name,folder_path)
            
        except Exception as err:
            logger.error("%s %s \n",__s_fn_id__, err)
            logger.debug(traceback.format_exc())
            print("[Error]"+__s_fn_id__, err)

        return rel_dir_path_


    ''' Function --- [DEPRECATE] GET EXTRACT DATA STORED PATH ---

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def get_extract_data_stored_path(
        self,
        data_store_path:str,
        parent_dir_name:str, 
        **kwargs):
        """
        Description:
            give the relative root strage location to amend a data & time specific
            folder for the current time. (_s3Storageobj or localhost directory path)
        Attributes:
           dirPath - string with folder path to the csv files
           **kwargs - contain the plance holder key value pairs
            columns: list
            start_date: datetime.date
            end_date: datetime.date
        Returns:
        Exceptions:
        """

        _search_data_save_dir = None
        _search_dt = datetime.now()
        _search_time_gap = self.scrapeTimeGap
        
        _s_fn_id = "function <get_extract_data_stored_path>"
        logger.info("Executing %s %s" % (self.__package__, _s_fn_id))

        try:
            if 'SCRAPE_TIME_GAP' in kwargs.keys():
                _search_time_gap = kwargs['SCRAPE_TIME_GAP']
            _parent_dir_path = os.path.join(data_store_path, parent_dir_name)

            if "SEARCH_DATETIME" in kwargs.keys():
                _search_dt = kwargs["SEARCH_DATETIME"]
            else:
                _search_dt = datetime.now()
            _search_dt = _search_dt + (datetime.min - _search_dt) % timedelta(minutes=_search_time_gap)

            ''' folder is a concaternation of date hour and minute;
                where minute < 30 --> 0 and 30 otherwise'''
            _dt_dir_name = str(_search_dt.year)+"-"+str(_search_dt.month)+"-"+str(_search_dt.day)\
                            +"-"+str(_search_dt.hour)+"-"+str(_search_dt.minute)+"/"     # csv file name
            _search_data_save_dir = os.path.join(_parent_dir_path, _dt_dir_name)
            ''' add the folder if not exists '''
            ''' TODO - fix this to check if defined in apps.cfg '''
            if kwargs['STORAGE_METHOD'] == 'local':
                if not os.path.exists(_parent_dir_path):
                    os.makedirs(_parent_dir_path)
                if not os.path.exists(_search_data_save_dir):
                    os.makedirs(_search_data_save_dir)
            elif kwargs['STORAGE_METHOD'] == 'AWS_S3':
                print("todo")
            else:
                raise ValueError("%s is an undefined storage location in **kwargs"
                                 % (kwargs['storageLocation']))

#            logger.info("Extracting data into %s storage", kwargs['storageLocation'])
            logger.info("OTA price data storage location: %s", _search_data_save_dir)
            logger.info("Search datetime set to: %s", str(_search_dt))

        except Exception as err:
            logger.error("%s %s \n", _s_fn_id, err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _search_data_save_dir

    ''' Function -- TODO --
            name: scrape_ota_to_csv
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''
    def scrape_data_to_csv(self,url,_scrape_tags_df,file_name, path):

        from bs4 import BeautifulSoup # Import for Beautiful Soup
        import requests # Import for requests
        import lxml     # Import for lxml parser
        import csv
        from csv import writer

        _s_fn_id = "function <scrape_data_to_csv>"
        logger.info("Executing %s", _s_fn_id)

        try:
            if _scrape_tags_df.shape[0] <= 0:
                raise ValueError("Invalid scrape tags no data scraped")
            if not file_name:
                raise ValueError("Invalid file name no data scraped")
            if not path:
                raise ValueError("Invalid path name no data scraped")

            ''' define generic header '''
            headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
            response = requests.get(url, headers=headers)
            # Make it a soup
            soup = BeautifulSoup(response.text,"lxml")
#            soup = BeautifulSoup(response.text,"html.parser")

            ''' extract the list of values from content block '''
            _cont_block = (_scrape_tags_df.loc[_scrape_tags_df['variable']=='content_block']).head(1)
            _l_scrape_text = soup.select(_cont_block.tag.item())

            if len(_l_scrape_text) <= 0:
                raise ValueError("no content block (area) for %s" %(_cont_block))

            ''' get the attribute list '''
            _l_col_names = list(_scrape_tags_df.variable)
            _l_col_names.remove('content_block')

            ''' init dataframe to store the scraped categorical text '''
            _prop_data_df = pd.DataFrame()

            ''' loop through the list to retrieve values from tags '''
            for row in _l_scrape_text:
                _scraped_data_dict = {}
                for colName in _l_col_names:
                    _tag = _scrape_tags_df.loc[_scrape_tags_df.variable==colName, 'tag'].item()
                    _code = _scrape_tags_df.loc[_scrape_tags_df.variable==colName, 'code'].item()

                    try:
                        _scraped_data_dict[colName] = row.find(_tag, class_ = _code).text

                    except Exception as err:
                        pass
                        
                if _scraped_data_dict:
                    _prop_data_df = pd.concat([_prop_data_df, pd.DataFrame(_scraped_data_dict, index=[0])])

        except Exception as err:
            logger.error("%s %s \n", _s_fn_id, err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _prop_data_df


    ''' Function
            name: scrape_url_list
            parameters:
                otaURLlist - string with folder path to the csv files
                **kwargs - contain the plance holder key value pairs
                            columns: list
                            start_date: datetime.date
                            end_date: datetime.date
            procedure: reads the all the csv files in the entire folder and
                        appends the data for the relevant columns defined in
                        the dictionary into a dataframe
            return dataframe (ota_bookings_df)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''

    def scrape_url_list(self,otaURLlist, searchDT: datetime, dirPath:str):

        saveTo = None   # init file name
        _l_saved_files = []

        _s_fn_id = "function <scrape_url_list>"
#        logger.info("Executing %s %s" % (self.__package__, _s_fn_id))

        try:
            if len(otaURLlist) > 0:
                logger.info("loading parameterized urls from list %d records", len(otaURLlist))
                print("loading parameterized urls from list %d records" % len(otaURLlist))
            else:
                raise ValueError("List of URLs required to proceed; non defined in list.")

            ''' loop through the list of urls to scrape and save the data'''
            for ota_dict in otaURLlist:
#                _ota_tags_df = _scrape_tags_df.loc[_scrape_tags_df['ota']==ota_dict['ota']]

                ''' file name is concaternation of ota name + location + checkin date + page offset and .csv file extension'''
                _fname = str(ota_dict['ota'])+"."+\
                        str(ota_dict['destination_id'])+"."+\
                        str(ota_dict['checkin'])+"."+\
                        str(ota_dict['page_offset']).zfill(3)+\
                        ".csv"
                _fname=_fname.replace(" ",".")

                ''' TODO add search_datetime'''
                if ota_dict['ota'] == 'booking.com':
                    saveTo = self._scrape_bookings_to_csv(
                        ota_dict['url'],      # constructed url with parameters
                        ota_dict['checkin'],  # booking intended checkin date
                        searchDT,   # date & time scraping was executed
                        ota_dict['destination_id'],  # destingation id to lookup the name
                        _fname,     # csv file name to store in
                        dirPath     # folder name to save the files
                    )
                    _l_saved_files.append(saveTo)

        except Exception as err:
            logger.error("%s %s \n", _s_fn_id, err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _l_saved_files

    ''' Function
            name: remove_empty_files
            parameters:
                dirPath - string with folder path to the csv files
                **kwargs - contain the plance holder key value pairs
                            columns: list
                            start_date: datetime.date
                            end_date: datetime.date
            procedure: reads the all the csv files in the entire folder and
                        appends the data for the relevant columns defined in
                        the dictionary into a dataframe
            return dataframe (ota_bookings_df)

            author: <nuwan.waidyanatha@rezgateway.com>
    '''

    def remove_empty_files(self,path):

        _s_fn_id = "function <remove_empty_files>"
#        logger.info("Executing %s %s" % (self.__package__, _s_fn_id))

        _l_removed_files = []
        try:
            if not path:
                raise ValueError("Undefined path to files, Abort removing files")

            for (dirpath, folder_names, files) in os.walk(path):
                for filename in files:
                    file_location = dirpath + '/' + filename  #location of the file
                    if os.path.isfile(file_location):
                        if os.path.getsize(file_location) == 0: # Checking if the file is empty or not
                            os.remove(file_location)            # remove empty files
                            _l_removed_files.append(filename)


        except Exception as err:
            logger.error("%s %s", _s_fn_id, err)
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _l_removed_files
