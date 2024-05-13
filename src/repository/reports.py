from fastapi import Depends, HTTPException, UploadFile, File
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.entity.models import User, Log
from typing import List
from src.conf import messages
from sqlalchemy import select, func, or_, extract , Boolean
from datetime  import date, datetime ,timezone
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

async def create_file_csv(filename, df):
    if filename == "report":
        filename = "src/import_csv/Report" + datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".csv"
    elif filename == "statistic":
        filename = "src/import_csv/Statistic" + datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".csv"
    '''
    Function of recording data in file *.csv

    :param filename (str): Filename.
    :return: A file
    '''
    df.to_csv (filename, index= False )

async def parsing_data(data):
    result = [[log.number, log.start, log.stop, log.billcash, log.billbalance, log.discount, log.in_parking ] for log in data]
    '''  
    Function of data parsing and writing to a list.

    :param data (sql session select): Request from database .
    :return: A list
    '''
    
    return result

async def statistics(data):
    data[['billcash', 'billbalance']] = data[['billcash', 'billbalance']].fillna(0)
    data['time_in_parkink'] = data.stop - data.start
    data['payment_amount'] = data.billcash + data.billbalance
    count = data['number'].value_counts()
    count = count.to_frame()
    time_in_parkink = data.groupby('number').agg('time_in_parkink')
    time_in_parkink = time_in_parkink.sum()
    result = time_in_parkink.to_frame()
    payment_amount = data.groupby('number').agg('payment_amount')
    payment_amount = payment_amount.sum()
    payment_amount = payment_amount.to_frame()
    result["payment_amount"] = payment_amount.iloc[:,0]
    result["number_of_times"] = count.iloc[:,0]
    print(result["number"].tolist())
    return result
 
async def get_avto_in_parking(limit, offset, user: User, db: AsyncSession = Depends(get_db)):  
    """
    Search function on a database of cars in the parking lot.

    :param limit (int): The maximum number of users in the function response.
    :param offset(int): The minimum number of users in the function response.
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A list
    """
    time_info = []
    info = select(Log).filter_by(in_parking=True).offset(offset).limit(limit)
    info = await db.execute(info)
    info = info.scalars().unique().all()
    datetime_naw = datetime.now(timezone.utc)
    result = [[log.number, log.start ] for log in info]
    for i in result:
        dict_ = {}
        dict_.update({'number_avto': i[0]})
        time_in_p = datetime_naw -  i[1]
        dict_.update({'start_time': i[1]})
        dict_.update({'time_in_parking': str(time_in_p) })
        time_info.append(dict_)
    return  time_info

async def get_reports_scv(import_csv, number, start_date, end_date,user: User, db: AsyncSession = Depends(get_db)):
    """
    Search function in the database of vehicle entry and exit logs with the ability to download a file scv/

    :param import_csv: bool: File upload condition
    :param number: str: car numb
    :param start_date: date: The minimum number of users in the function response.
    :param end_date: date: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A  list
    """
    columns = ["number", "start", "stop", "billcash", "billbalance", "discount", "in_parking"]

    if number == None:
        info = select(Log)
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            await create_file_csv("report",data_df)
        return returned_list
    elif start_date != None and end_date == None:
        info = select(Log).filter_by(number = number).\
        filter((extract('year',Log.start) >= start_date.year)).\
        filter((extract('month', Log.start) >= start_date.month)).\
        filter((extract('day', Log.start) >= start_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            await create_file_csv("report",data_df)
        return returned_list
    elif start_date == None and end_date != None:
        info = select(Log).filter_by(number = number).\
            filter((extract('year',Log.start) <= end_date.year)).\
            filter((extract('month', Log.start) <= end_date.month)).\
            filter((extract('day', Log.start) <= end_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            await create_file_csv("report",data_df)
        return returned_list
    elif start_date != None and end_date != None:
        info = select(Log).filter_by(number = number).\
            filter((extract('year',Log.start) >= start_date.year)).\
            filter((extract('month', Log.start) >= start_date.month)).\
            filter((extract('day', Log.start) >= start_date.day)).\
            filter((extract('year',Log.start) >= end_date.year)).\
            filter((extract('month', Log.start) >= end_date.month)).\
            filter((extract('day', Log.start) >= end_date.day))
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            await create_file_csv("report",data_df)
        return returned_list
    else :
        stmt = select(Log).filter_by(number = number)
        stmt = await db.execute(stmt)
        info = stmt.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            await create_file_csv("report",data_df)
        return returned_list

async def get_statistics(import_csv, number, start_date, end_date,user: User, db: AsyncSession = Depends(get_db)): 
    """
    Search function in the database of vehicle entry and exit logs with the ability to download a file scv/

    :param import_csv: bool: File upload condition
    :param number: str: car numb
    :param start_date: date: The minimum number of users in the function response.
    :param end_date: date: Get the connection to the database
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A users object
    """
    columns = ["number", "start", "stop", "billcash", "billbalance", "discount", "in_parking"]

    if number == None:
        info = select(Log)
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns) 
            res = await  statistics(data_df)
            await create_file_csv('statistics',res)
        return returned_list
    elif start_date != None and end_date == None:
        info = select(Log).filter_by(number = number).\
        filter((extract('year',Log.start) >= start_date.year)).\
        filter((extract('month', Log.start) >= start_date.month)).\
        filter((extract('day', Log.start) >= start_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns)
            res = await  statistics(data_df)
            await create_file_csv('statistics',res)
        return returned_list
    elif start_date == None and end_date != None:
        info = select(Log).filter_by(number = number).\
            filter((extract('year',Log.start) <= end_date.year)).\
            filter((extract('month', Log.start) <= end_date.month)).\
            filter((extract('day', Log.start) <= end_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns)
            res = await  statistics(data_df) 
            await create_file_csv('statistics',res)
        return returned_list
    elif start_date != None and end_date != None:
        info = select(Log).filter_by(number = number).\
            filter((extract('year',Log.start) >= start_date.year)).\
            filter((extract('month', Log.start) >= start_date.month)).\
            filter((extract('day', Log.start) >= start_date.day)).\
            filter((extract('year',Log.start) >= end_date.year)).\
            filter((extract('month', Log.start) >= end_date.month)).\
            filter((extract('day', Log.start) >= end_date.day))
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns)
            res = await  statistics(data_df) 
            await create_file_csv('statistics',res)
        return returned_list
    else :
        stmt = select(Log).filter_by(number = number)
        stmt = await db.execute(stmt)
        info = stmt.scalars().unique().all()
        returned_list =  await parsing_data(info)
        if import_csv == True:
            data_df = pd.DataFrame(returned_list,columns = columns)
            res = await  statistics(data_df) 
            await create_file_csv('statistics',res)
        return returned_list


