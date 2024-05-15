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
from fastapi.responses import FileResponse

async def create_file_csv(filename, df):
    if filename == "report":
        filename = "src/reports/Report.csv" #+ datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".csv"
        f = 'Report.csv'
    elif filename == "statistics":
        filename = "src/reports/Statistics.csv" #+ datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".csv"
        f = 'Statistic.csv'
    '''
    Function of recording data in file *.csv

    :param filename (str): Filename.
    :return: A file
    '''
    df.to_csv (filename, index= True )
    return FileResponse(path=filename, filename=f,  media_type='multipart/form-data')


async def parsing_data(data):
    result = [[log.number, log.start, log.stop, log.discount, log.total, log.in_parking] for log in data]
    '''  
    Function of data parsing and writing to a list.

    :param data (sql session select): Request from database .
    :return: A list
    '''
    
    return result

async def statistics(data):
    data[['total']] = data[['total']].fillna(0)
    data[['stop']] = data[['stop']].fillna(datetime.now(timezone.utc))
    data['time_in_parkink'] = data.stop - data.start
    data['number_avto'] = data['number']
    count = data['number'].value_counts()
    count = count.to_frame()
    time_in_parkink = data.groupby('number').agg('time_in_parkink')
    time_in_parkink = time_in_parkink.sum()
    result = time_in_parkink.to_frame()
    payment_amount = data.groupby('number').agg('total')
    payment_amount = payment_amount.sum()
    payment_amount = payment_amount.to_frame()
    result["total"] = payment_amount.iloc[:,0]
    result["number_of_times"] = count.iloc[:,0]
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
    time_info.append({"Free parking spaces": 100 - len(info)})
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

async def get_reports_scv(number, start_date, end_date, db: AsyncSession = Depends(get_db)):
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
    columns = ["number", "start", "stop", "discount", "total", "in_parking"]
    if number == None:
        info = select(Log)
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list, columns = columns) 
        file = await create_file_csv("report",data_df)
        return file
    elif start_date != None and end_date == None:
        info = select(Log).filter_by(number = number).\
        filter((extract('year',Log.start) >= start_date.year)).\
        filter((extract('month', Log.start) >= start_date.month)).\
        filter((extract('day', Log.start) >= start_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list,columns = columns) 
        file = await create_file_csv("report",data_df)
        return file
    elif start_date == None and end_date != None:
        info = select(Log).filter_by(number = number).\
            filter((extract('year',Log.start) <= end_date.year)).\
            filter((extract('month', Log.start) <= end_date.month)).\
            filter((extract('day', Log.start) <= end_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list,columns = columns) 
        file = await create_file_csv("report",data_df)
        return file
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
        data_df = pd.DataFrame(returned_list,columns = columns) 
        file = await create_file_csv("report",data_df)
        return file
    else :
        stmt = select(Log).filter_by(number=number)
        stmt = await db.execute(stmt)
        info = stmt.scalars().unique().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list,columns = columns) 
        file = await create_file_csv("report",data_df)
        return file

async def get_statistics( number, start_date, end_date,user: User, db: AsyncSession = Depends(get_db)): 
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
    columns = ["number", "start", "stop", "discount", "total", "in_parking"]

    if number == None:
        info = select(Log)
        info = await db.execute(info)
        info = info.scalars().unique().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list,columns = columns) 
        res = await statistics(data_df)
        file = await create_file_csv('statistics',res)
        return file
    elif start_date != None and end_date == None:
        info = select(Log).filter_by(number = number).\
        filter((extract('year',Log.start) >= start_date.year)).\
        filter((extract('month', Log.start) >= start_date.month)).\
        filter((extract('day', Log.start) >= start_date.day))
        info = await db.execute(info)
        info = info.scalars().all()
        returned_list =  await parsing_data(info)
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
        data_df = pd.DataFrame(returned_list,columns = columns)
        res = await  statistics(data_df) 
        await create_file_csv('statistics',res)
        return returned_list
    else :
        stmt = select(Log).filter_by(number = number)
        stmt = await db.execute(stmt)
        info = stmt.scalars().unique().all()
        returned_list =  await parsing_data(info)
        data_df = pd.DataFrame(returned_list,columns = columns)
        res = await  statistics(data_df) 
        await create_file_csv('statistics',res)
        return returned_list


