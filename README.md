# Exchange-Matching

A piece of software which will match buy and sell orders for a stock/commodities market.

## How to run server

switch to the `erss-hwk4-hy201-ht175/docker-deploy` directory

run

```bash
sudo docker-compose up
```

## How to run test

1. Unit test

   A coverage test that ensure sequence result and function correctness

   switch to the `erss-hwk4-hy201-ht175/docker-deploy/testing` directory

   run

   ```bash
   python3 client.py > FILENAME.xml
   ```

2. workload test

   High workload test that sending 600 requests using 100 clients, the requests including create account, create position, create transaction, cancel transaction, make transaction between 2 transactions, query a transaction.

   switch to the `erss-hwk4-hy201-ht175/docker-deploy/testing` directory

   run

   ```bash
   python3 workloadTest.py
   ```

   The result is in the `workloadTestResult.xml` file.

   > **!Attention**
   >
   > The graphing part involves resetting the database, therefore, it cannot connect the database in the docker. To run a graph, please run the server locally. The graph part have no difference with current test except without writing the output and reset database (to do the different workload test and ensure the result is same)

3. Scalability Test

   change process pool size: `PROCESSNUM` in `src/server.py`

   change core number, modify the instruction in the `src/run.sh` replace `python3 server.py` with

   ```bash
   taskset -c 0 python3 server.py
   or
   taskset -c 0-1 python3 server.py
   or
   taskset -c 0-3 python3 server.py
   ```

   

4. Write your own

   check the `xml_request_generator.py` & `workloadTest.py` to write your own unit and concurrency test. 