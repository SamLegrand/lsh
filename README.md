# IR assignment 3: Plagiarism detection system

## Getting ready
### Installing requirements
The following libraries, which can be found in [requirements.txt](./requirements.txt), are needed to run the code. 
* matplotlib
* pandas

### Creating configuration file
To be able to run the code, a file called `usersettings.py` will have to be created inside the [src](./src) folder. This file dictates the amount of threads the system can use, the content should be in following format:
```
usersettings = {
    "threads": 8    # change this to change the number of CPU threads used in places that can utilize multiple threads
}
```

## Obtaining the results

The [results](./results.csv) can be computed by running the `lsh.py` file. 

The s-curve plots can be obtained by executing `sim_analysis.py`. To compute the performance, specificity, sensitivity and precision metrics for the plagiarism detection, the `lsh_analysis.py` file can be run.
