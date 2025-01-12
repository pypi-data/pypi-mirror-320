import numpy as np
import os
from mpi4py import MPI


def running_mean(x, N):
    '''

    Parameters
    ----------
    x : ndarray
        1d array.
    N : int
        Number of elements used to smooth.

    Returns
    -------
    1d array
        Smoothed array.

    '''
    cumsum = np.nancumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


def nanravel(matrix):
    '''
    Return a contiguous flattened array without nan.

    Parameters
    ----------
    matrix : ndarray
        Input array.

    Returns
    -------
    matrix : 1d array
        Flattened array.

    '''
    matrix = np.ravel(matrix)
    matrix = matrix[np.logical_not(np.isnan(matrix))]
    return matrix

def listdir(path, suffix, suffix_on=True, prefix_on=False):
    '''
    Return a list containing the names of the files in the directory.
    Filter path with specific suffix(or prefix). This is a improved version of os.listdir

    Parameters
    ----------
    path : string
        Input path.
    suffix : string
        Suffix or prefix.
    suffix_on : bool, optional
        Whether to use suffix. The default is 1.
    prefix : TYPE, optional
        Whether to use suffix. The default is 0.

    Returns
    -------
    ls : list
        A list containing the names of the files in the directory with specific suffix or prefix.

    '''
    tem = os.listdir(path)
    if prefix_on == True:
        num = len(suffix)
        ls = np.array([])
        for p in tem:
            if p[:num] == suffix:
                ls = np.append(ls, p)
    else:
        if suffix_on == True:
            num = len(suffix)
            ls = np.array([])
            for p in tem:
                if p[-num:] == suffix:
                    ls = np.append(ls, p)

    return ls



def nanaverage(data,weights=0,axis=9999):
    '''
    Weighted mean for array with nan.

    Parameters
    ----------
    data : ndarray
        Input data.
    weights : nadarry, optional
        DESCRIPTION. The default is 0.
    axis : TYPE, optional
        DESCRIPTION. The default is 100.

    Raises
    ------
    ValueError
        the data and weights are expected to have the same shape and nan values.

    Returns
    -------
    TYPE
        Weighted mean.

    '''
    axis = np.array([axis])
    if np.all(axis == 9999):
        axis = np.arange(len(data.shape))
    if np.all(weights==0):
        weights = np.copy(data)
        weights[:]=1
    if data.shape != weights.shape:
        raise ValueError('data and weights have different shape')
    if len(nanravel(weights)) != len(nanravel(data)):       
        weights[np.isnan(data)]=np.nan
        print('Length different! Assign nan to weights where data eq nan')
    if len(nanravel(weights)) != len(nanravel(data)):
        raise ValueError('data and weights have different nan')
    tem1 = np.nansum(data*weights,axis=tuple(axis))
    tem2 = np.nansum(weights,axis=tuple(axis))
    return tem1/tem2


def arrayinfo(array,detail=False):
    '''
    Print array info for ndarray.

    Parameters
    ----------
    array : ndarray
        Input array.
    detail : bool, optional
        Whether to print detailed info of the array. The default is False.

    Returns
    -------
    None.

    '''
    if type(array) != np.ndarray:
        print("It's not an numpy.ndarray")
        return None
    array_max = np.max(array)
    if np.isnan(array_max):
        print('Nan exists\nmaxium:{:.2f}'.format(np.nanmax(array)))
        print('minmium:{:.2f}'.format(np.nanmin(array)))
    else:
        print('Nan not exists\nmaxium:{:.2f}'.format(array_max))
        print('minmium:{:.2f}'.format(np.min(array)))
    print('shape:', array.shape)
    print('dtype:', array.dtype)
    if detail:
        print('Unique value:',np.unique(array))
        print('Mean:',np.nanmean(array))
        print('Std:',np.nanstd(array))




def exclude_outlier(in_array):
    '''
    Exclude outlier (3 sigma)

    Parameters
    ----------
    array : 1d array
        Input data.

    Returns
    -------
    array : 1d array
        Output data with outlier=np.nan.

    '''
    array = np.copy(in_array)
    arraystd = np.nanstd(array, ddof=1)
    arraymean = np.nanmean(array)
    arrayoutlier = np.where(np.abs(array - arraymean) > (3 * arraystd))
    print(array[arrayoutlier])
    print(arraystd)
    array[arrayoutlier] = np.nan
    return array

'''
220422 
It seems that the outlier will be eventually excluded in a few loops
n = np.zeros((1000))
for i in range(1000):
    aa = np.random.normal(100,10,20000)
    bb = exclude_outlier(aa)
    while np.nanstd(aa, ddof=1) != np.nanstd(bb, ddof=1):
        aa = bb
        bb = exclude_outlier(aa)
        n[i] = n[i]+1
'''

def r2a(rasterfn,dtype = None,bandnum=1):
    from osgeo import gdal
    '''
    Convert raster to array

    Parameters
    ----------
    rasterfn : String
        raster file path.
    dtype : String
        date type: int, int8, float, float32, etc.
    bandnum  : Int
        number of band, default=1

    Returns
    -------
    2d-ndarray
        numpy array from raster band 1.

    '''
    if dtype==None:
        raster = gdal.Open(rasterfn)
        ra = raster.GetRasterBand(bandnum).ReadAsArray()
    else:
        raster = gdal.Open(rasterfn)
        ra = raster.GetRasterBand(bandnum).ReadAsArray()
        ra = ra.astype(dtype)
    return ra


def n2a(ncfile,var_name):
    '''
    Convert nc to array

    Parameters
    ----------
    ncfile : String
        NC file path.
    var_name : String
        Variable name.

    Returns
    -------
    array : TYPE
        DESCRIPTION.

    '''
    from netCDF4 import Dataset
    nc = Dataset(ncfile, 'r')
    array = np.copy(nc.variables['{}'.format(var_name)][:])
    nc.close()
    return array

def nans(shape)：
    '''
    Same as np.zeros but filled with nan

    Parameters
    ----------
    shape : int or tuple of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.

    Returns
    -------
    array : ndarray
        Array of zeros with the given shape, dtype, and order.

    '''
    array = np.zeros(shape)
    array[:] = np.nan

    return array



# currently not used 
def func_replace(filein_func, name_func, idx_func, value_func):
  import re
  with open(filein_func, 'r') as fin_func:
    lines_func = fin_func.readlines()
    flag = 0
    for i_func, line_func in enumerate(lines_func):
      if re.match(name_func, line_func):
        lines_func[i_func] = line_func[:idx_func] + str(value_func) +'\n'
        flag += 1
    if flag==0:
      print('Cannot find %s'%name_func)
  fin_func.close()
  with open(filein_func, 'w') as fin_func:
    fin_func.writelines(lines_func)
  fin_func.close()


def func_to_landpoint(lat, lon, res=0.5):
  '''
  This is to convert real lat, lon to landpoint value in CRU-NCEP forcing file.
  ilat, ilon mean python index starting from 0 [90, -180].
  landpoint starting from 1.
  '''
  ilat = int((90-lat) / res)
  ilon = int((lon+180) / res)
  landpoint = int(ilat*360/res + ilon + 1)
  return landpoint

def func_to_ilatilon(landpoint, res=0.5):
    '''
    This is to convert landpoint value in CRU-NCEP forcing file to index of lat and lon
    ilat, ilon mean python index starting from 0 [90, -180].
    landpoint starting from 1.
    '''
    ilat = int((landpoint-1) / (360/res))
    ilon = int(landpoint-ilat*360/res-1)
    return ilat, ilon

def func_to_latlon(landpoint, res=0.5):
    '''
    This is to convert landpoint value in CRU-NCEP forcing file to lat and lon
    ilat, ilon mean python index starting from 0 [90, -180].
    landpoint starting from 1.
    '''
    ilat = int((landpoint-1) / (360/res))
    lat = 90 - res*ilat
    ilon = int(landpoint-ilat*360/res-1)
    lon = 180 + res*ilon
    return lat, lon

def remplace(filein,name,value):
    import re
    with open(filein, 'r') as fin:
        lines = fin.readlines()
        flag = 0
        for ilines, line in enumerate(lines):
            if re.match(name, line):
                lines[ilines] = '{}={}'.format(name,value)+'\n'
        flag += 1
    if flag==0:
        print('Cannot find {}'.format(name))
    fin.close()
    with open(filein, 'w') as fin:
        fin.writelines(lines)
    fin.close()

remplace('config.card','JobName',val_name)





def run(func, size_para):
    '''
    Automatically distribute parameters to each cpu

    Parameters
    ----------
    func : TYPE
        The function for parallel computing
    size_para : int
        The number of paramters that will be distributed
    size_cpu : int
        The number of cpu used for parallel computing

    Returns
    -------
    array : TYPE
        DESCRIPTION.

    '''
    # Record the start time
    if rank == 0:
        total_start_time = time.time()
        print(f"Task began at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if rank == 0:
        task_queue = list(range(file_len))
        task_index = 0
        completed_tasks = 0
        # Assign an initial task to each worker process
        for i in range(1, size):
            if task_index < len(task_queue):
                comm.send(task_queue[task_index], dest=i, tag=1)
                task_index += 1
        while completed_tasks < file_len:
            # Receive a completed task signal from a worker process
            status = MPI.Status()
            finished_task = comm.recv(source=MPI.ANY_SOURCE, tag=2, status=status)
            completed_tasks += 1
            worker_rank = status.Get_source()
            # Assign a new task
            if task_index < len(task_queue):
                comm.send(task_queue[task_index], dest=worker_rank, tag=1)
                task_index += 1
            else:
                comm.send(None, dest=worker_rank, tag=0)  # No more tasks, send termination signal
    else:
        while True:
            # Receive a task from the master process
            task = comm.recv(source=0, tag=MPI.ANY_TAG, status=MPI.Status())
            if task is None:
                break  # No more tasks, exit the loop
            func(task)
            comm.send(task, dest=0, tag=2)  # Notify the master process that the task is completed
    comm.Barrier()  # Add a synchronization point to ensure all processes synchronize here
    # Record the end time and calculate the elapsed time
    print(f"Process {rank} completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if rank == 0:
        total_end_time = time.time()
        total_elapsed_time = total_end_time - total_start_time
        print(f"Total time taken for the entire task: {total_elapsed_time:.2f} seconds")
    MPI.Finalize()  # Properly close the MPI environment


def month(acc=True):
    mon = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    if acc:
        return np.cumsum(mon)
    else:
        return mon[1:]

def nanaverage(data,axis=(0,1),weights=0):
    weights0 = np.copy(weights)
    weights0[np.isnan(data)]=np.nan
    tem1 = np.nansum(data*weights0,axis=axis)
    tem2 = np.nansum(weights0,axis=axis)
    return tem1/tem2


def w_std(array,weights=0):
    mean = nanaverage(array,axis=(0,1),weights = weights)
    std0 = np.sqrt(nanaverage((array-mean)**2,axis=(0,1),weights = weights))
    return std0






