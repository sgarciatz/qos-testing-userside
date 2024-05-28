# QoS Testing server

This application is intended to be used in conjunction with the one from https://github.com/sgarciatz/qos-testing-server/tree/main, which is its "backend".

When this app is executed it makes requests to the endpoints of the server side. The requests and responses are used to measure QoS metrics such as latency and jitter. An SQLite3 instance is created in the database folder to guarantee its persistence.

The app has two execution modes, one for carrying out experiments, and the other to only see the results of existing experiments in the database.

In order to parametrize the execution of the app JSON files are used. They have the following format:

```
{
    "experiment_name": "whatever_name_00",
    "experiment_description": "A descriptive explanation of the experiment carried out so as not to forget its purpose or usefulness.",
    "server_ip": "192.168.122.1",
    "server_port": "8080",
    "method": "POST",
    "payload_size": 10000000,
    "n_requests": 10
}
```
The payload is specified in Bytes in the `payload_size` field and `n_requests` specifies the the number of sequential requests that are to be made. The `method` attribute can be assigned the value `POST` or `GET`. In the current state of the application, `POST`-based experiments have the same outgoing (request) and ingoing (response) `payload_size`. On the other hand, `GET`-based experiments can have "no payload" (very little) or payload in incoming responses only.

## Execution guide
To set up the enviroment execute the following commands:

``` 
cd <wherever/the/git/repository/is/cloned>
pip install -e requirements.txt
```

If you want to execute make sure you are in the `src` folder:

```
cd ./src
```

Execute the followinng command to carry out an experiment

``` 
python client.py <path_to_json_file>
```

Use the flag `results` if you only want to see the results of an existing experiment:

```
python client.py <path_to_json_file> --results
```