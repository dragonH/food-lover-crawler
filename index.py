"""
    This script is to crawl food lover
"""

import requests
import pandas as pd
import logging
import time
from typing import List
import os
from datetime import datetime

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_current_time():
    """
        This function is to get current time
    """
    current_time = datetime.now()
    return current_time

def defined_variables():
    """
        This function is to defined variables
    """
    category_object = ['餐飲', '糕餅', '夜市小吃/市場']
    zone_object = {
        "雙北": ["臺北市", "新北市", "基隆市"],
        "桃竹苗": ["桃園市", "新竹市", "新竹縣", "苗栗縣"],
        "中彰投": ["臺中市", "彰化縣", "南投縣"],
        "雲嘉南": ["雲林縣", "嘉義市", "嘉義縣", "臺南市"],
        "高屏": ["高雄市", "屏東縣"],
        "宜蘭": ["宜蘭縣"],
        "花蓮": ["花蓮縣"],
        "台東": ["臺東縣"],
        "金馬離島": ["澎湖縣", "金門縣", "連江縣"]
    }
    return category_object, zone_object

def get_data_from_url(
    _url: str,
    _params: dict,
    _retry_times: int = 0
):
    """
        This function is to get data from url
    """
    try:
        if _retry_times:
            logger.info('Retry times: %s', _retry_times)
        delay_time = _retry_times ** 0.6
        time.sleep(delay_time)
        response = requests.get(
            url = _url,
            params = _params
        )
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
    except Exception as error:
        logger.error(error)
        _retry_times += 1
        get_data_from_url(
            _url = _url,
            _params = _params,
            _retry_times = _retry_times
        )

def create_partition_folder(
    _current_time: datetime
):
    """
        This function is to create partition folder
    """
    try:
        logger.info('Start to create partiton folder...')
        # path = os.path.join('./datas', str(_current_time.year), str(_current_time.month), str(_current_time.day))
        path = f'./datas/{str(_current_time.year)}/{str(_current_time.month)}/{str(_current_time.day)}'
        os.makedirs(path)
        logger.info('Finish creating partiton folder')
        return path
    except FileExistsError:
        logger.info('Partiton folder exists. Skip...')
        return path

def write_data_as_csv(
    _all_data: List[dict],
    _current_time: datetime,
    _partition_path: str
):
    """
        This function is to write data as csv
    """
    logger.info('Start to write data as csv...')
    current_time_string = _current_time.strftime('%Y%m%d%H%M%S')
    df = pd.DataFrame(_all_data).drop(columns = ['index']).reset_index()
    df.to_csv(f'{_partition_path}/{current_time_string}.csv', index = False, sep = '|')
    logger.info(f'Finish writing data as csv. File name {_partition_path}/{current_time_string}.csv')

def main():
    """
        This is main function
    """
    try:
        current_time = get_current_time()
        logger.info('Start to crawl data...')
        category_object, zone_object = defined_variables()
        all_data = []
        partition_path = create_partition_folder(
            _current_time = current_time
        )
        for category in category_object:
            for zone in zone_object.keys():
                for city in zone_object[zone]:
                    logger.info('Crawling: %s %s %s', category, zone, city)
                    url = 'https://foodlover.tw/goodfood/query/shop'
                    params = {
                        "category": category,
                        "zone": zone,
                        "city": city,
                        "pay_tool": ['信用卡', '行動支付', '電子票證']
                    }
                    data = get_data_from_url(
                        _url = url,
                        _params = params
                    )
                    all_data += data
        write_data_as_csv(
            _all_data = all_data,
            _current_time = current_time,
            _partition_path = partition_path
        )
        logger.info('Finish crawling data')
    except:
        raise

if __name__ == '__main__':
    main()