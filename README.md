# KaloomMetricExtraction
The extraction tool of the Kalloom's Merge Request

### Installationof  

Please install Dependencies from requirement.txt
```
pip install -r requirements.txt
```

#### Code execution
```
python .\main_api.py -f .\config.json
```

#### Configuration file

This project works with a configuration file 


```
{
    "parameters": {
        "MR_ID": 0,
        "project_ids": [   **-> The id of the projects that will be extracted**
            29738620,
            3472737
        ],
        "start_Date_Vizu": "2023-06-25T06:01:58.041Z", **-> The start date of the interval**
        "end_Date_Vizu": "2023-06-27T13:27:58.174Z",  **-> The finish date of the interval**
        "days_per_sprint": 1,
        "get_all_project": false **-> If true, the whole project will be extracted, if not, only the date interval will be extracted**
    },
    "gitlab": {
        "auth_token": "glpat-YhUuMY-BYrEqCzcV2fzR",
        "base_url": "https://gitlab.com"
    }
}

```
