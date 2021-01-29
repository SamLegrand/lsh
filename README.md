# IR assignment 3: Plagiarism detection system

The report can be found [here](./report.pdf).

## LSH features
### Index creation
The LSH class can compute a LSH index from a given csv document. We can customize the signature set size `M` and amount of rows in each band `r`. We can also modify the hash function being used for the minhashing operation. This pre-processes the documents according to what is specified in the report.

### Storing/loading index
The LSH class can store the computed index to a json file, this can be helpful for big datasets where computing the index takes a long time. The index can of course be loaded again from the json file. 

### Querying
Custom queries can be executed on the index, to find out if the queried document is plagiarized.

### Finding near-duplicates inside data set
The LSH class is able to detect and save all near-duplicate documents inside the dataset to a csv file.

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

The [results](./result.csv) can be computed by running the `lsh.py` file. 

The s-curve plots can be obtained by executing `sim_analysis.py`. To compute the performance, specificity, sensitivity and precision metrics for the plagiarism detection, the `lsh_analysis.py` file can be run.
