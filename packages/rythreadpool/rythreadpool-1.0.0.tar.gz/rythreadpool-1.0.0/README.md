# ThreadPool library
- Multi-threading library 
- Allows to limit the number of threads to a fixed number

## Install
```
pip install rythreapool
```

## Usage
- import the library
```python
import threadpool
```
- create a new ThreadPool, giving as argument the number of desidred parallel threads
  - it is suggested to never exceed the number of physical threads that your processor has
```python
pool = threadpool.ThreadPool(16)
```
- now it is possible to run multiple functions or tasks 
```python
pool.execute(fn=myTask, args=())
```
- to check if the threadpool is busy, use the following function
  - returns `True` if the pool is working, otherwise returns `False`
```python
pool.isWorking()
```

### Notes
1. remember that, if a task implements active waiting, it will keep its thread busy until the end of execution
2. once reaced the limit of parallel threads, all the following tasks will have to wait for a thread to become free