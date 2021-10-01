import os, time
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
DEFAULT_FORMAT = ['success_tag','info_type', 'info']

class log_manager():
    '''
    logging tool
    format like (default format, the first column is default to time):
    time, SUCCESS, info_type , info;
    time, ERROR, info_type, info;
    save in txt file format
    
    Attributes:
        logging_file (str): full path of logging file
        logging_format (list): the items need to be logged
    '''
    def __init__(self, logging_file, logging_format=DEFAULT_FORMAT):
        '''
        Args:
            logging_file (str): full path of logging file
            logging_format (list): the items need to be logged
        '''
        self.logging_file = logging_file
        self.logging_format = ['time'] + logging_format
        
        # init method
        self.init_log()
    def init_log(self):
        '''
        create log file
        '''
        if not os.path.exists(self.logging_file):
            init_str = ','.join([i for i in self.logging_format])
            with open(self.logging_file, 'a+') as f:
                f.write('{};'.format(init_str))
    def gen_time(self):
        '''
        Returns:
            string, time
        '''
        localtime = time.localtime(time.time())
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', localtime)
        return time_str
    def write_log(self, info, success=True, info_type='notype', printout=True, add_to_list=None):
        '''
        this function is for default format
        
        Args:
            info (str): the log
            success (bool)
            info_type (str): Defaults to 'notype'
            printout (bool): whether to print the log. Default to True
            add_to_list (list): Defaults to None
        Returns:
            dict: return the log dict
        '''
        logging = {}
        
        logging['time'] = self.gen_time()
        if success:
            logging['success_tag'] = 'SUCCESS'
        else:
            logging['success_tag'] = 'ERROR'
        logging['info_type'] = info_type
        logging['info'] = info
        list_log = []
        for i in self.logging_format:
            list_log.append(logging[i])
        log_text = ','.join(list_log)
        with open(self.logging_file, 'a') as f:
            f.write(log_text+';')
        if printout:
            print(log_text.replace(',','  '))
        if add_to_list != None:
            add_to_list.append(info.strip())
            
        return logging
    
    def get_info_list(self,info_wanted='info', **kwargs):
        '''
        gain a info list
        specifical for default format
        Args:
            **kwargs: the selection condition, for example: success_tag='SUCCESS', info_type='notype'
        Returns:
            list, 
        '''
        with open(self.logging_file, 'r') as f:
            logging_content = f.read()
        logging_content = logging_content.replace(';',os.linesep)
        df = pd.read_table(StringIO(logging_content), sep=',',error_bad_lines=False)
        if kwargs:
            for k in kwargs.keys():
                try:
                    df = df[df[k]==kwargs[k]]
                except:
                    print('no column name {}'.format(k))
        list_results = df[info_wanted].values.tolist()
        print('the len of list: {}'.format(len(list_results)))
        return list_results

if __name__ == '__main__':
    lm = log_manager('logtest.txt')
    lm.write_log('test log')
    lm.write_log('test Error', success=False)
    success_list = lm.get_info_list(success_tag='SUCCESS')
    print(success_list)
    error_list = lm.get_info_list(success_tag='ERROR')
    print(error_list)
