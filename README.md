# Preface
This repository's purpose is to highlight the issue with regards to the usage of DVC's `run-cache`. As highlighted in [this discussion](https://discuss.dvc.org/t/dvc-1-0-release/412/5), `run-cache` is supposed to have a long memory of runs. Any changes to code and parameters for which its values have been used (executed) before, with or without commits, `dvc repro` will comb through the run caches and retrieves the output(s) that matches the version of the code and parameters that is being accounted for.

# Issue
This repository aims to highlight a shortcoming of this feature: the `run-cache` feature is not able to retrieve the output pertaining to a set of parameters that has been executed before, in another machine, even after executing `dvc pull` with the flags `--run-cache` and `--all-commits`.

# Reproducing the Issue

## Environment

OS Specs:
+ osx-64

Python environment:
+ Python 3.6.8
+ pandas==1.1.4
+ pyyaml=5.3.1

This feature was tested with the following DVC version:
```
$ dvc version
DVC version: 1.9.1 (brew)
---------------------------------
Platform: Python 3.9.0 on macOS-10.14.6-x86_64-i386-64bit
Supports: azure, gdrive, gs, http, https, s3, ssh, oss, webdav, webdavs
```

Remote Storage Types tested on:
+ Azure Blob Storage
+ Aliyun OSS

## Steps to Reproduce Issue

### Summary of steps:
1. Clone Git repository.
2. Initialise DVC.
3. Set up DVC remote.
4. Add data to DVC and push to remote.
5. Run a data processing step that generates and output, following a set parameter, and push to DVC remote.
6. Repeat step 5 with another parameter value and push to DVC remote.
7. Git push.
8. Navigate to a separate folder location (or use a separate machine) and clone the same repository.
9. Reconfigure DVC remote.
10. Pull run cache from DVC remote.
11. Change parameter to one that is used in step 5 and DVC repro.

__Step 1:__ Fork Git repository that contains the relevant code.
First and foremost, fork [https://github.com/ryzalk/test-dvc-rc-pub](https://github.com/ryzalk/test-dvc-rc-pub) and then clone that fork to your machine.
```bash
$ git clone https://github.com/<YOUR_GIT_USER_ID>/test-dvc-rc-pub.git
```

__Step 2:__ Initialise DVC.
```bash
$ cd test-dvc-rc-pub
$ dvc init
$ git commit -m "DVC init."
```

__Step 3:__ Set up DVC remote.
```bash
# Set up your own DVC data remote here
# Commands for setting up Azure remote
$ dvc remote add -d azremote azure://dvc-remote/test-dvc-rc
$ dvc remote modify --local azremote connection_string <YOUR_AZ_CONN_STRING_HERE>
$ git add .dvc/config
$ git commit -m "Configure default DVC remote storage."
```

__Step 4:__ Add `titanic.csv` data.
```bash
$ dvc import-url https://ryzalkdev.blob.core.windows.net/ryzal-pub-misc/titanic.csv
$ git add titanic.csv.dvc .gitignore
$ git commit -m "Add titanic data."
$ dvc push
```

__Step 5:__ Add `slice` stage through `dvc run`.
```bash
# This stage/script basically slices the original data and outputs it to another `.csv` file.
# Current 'num_rows' parameter value: 200
$ dvc run -n slice \
    -d titanic.csv -d slice-data.py \
    -o sliced_data.csv \
    -p test-params.yaml:num_rows \
    python slice-data.py
$ git add dvc.lock dvc.yaml .gitignore
$ git commit -m "Add slice data stage."
$ dvc push --run-cache
```

__Step 6:__ Run the `slice` stage through `dvc repro` with a different parameter value.
```bash
$ sed -i '' 's/num_rows: 200/num_rows: 500/' test-params.yaml
# If you're using Linux
# sed -i 's/num_rows: 200/num_rows: 500/' test-params.yaml
# Current 'num_rows' parameter value: 500
$ dvc repro
$ git add dvc.lock test-params.yaml
$ git commit -m "Slice 500 data points."
$ dvc push --run-cache
```

__Step 7:__ Push all changes to Git remote.
```bash
$ git push
```

__Step 8:__ Navigate to a separate folder location (or use a separate machine) and clone the same repository.
```bash
$ git clone https://github.com/<YOUR_GIT_USER_ID>/test-dvc-rc-pub.git
```

__Step 9:__ Add credentials for usage of DVC remote.
```bash
$ dvc remote modify --local azremote connection_string <YOUR_AZ_CONN_STRING_HERE>
```

__Step 10:__ Pull run caches from DVC remote.
```bash
$ dvc pull --run-cache --all-commits
```

__Step 11:__ Change parameter to one that is used in step 6 and DVC repro.
```bash
$ sed -i '' 's/num_rows: 500/num_rows: 200/' test-params.yaml
# If you're using Linux
# sed -i 's/num_rows: 500/num_rows: 200/' test-params.yaml
# Current 'num_rows' parameter value: 200
$ dvc repro
```

### Outcome
The issue is considered reproduced/replicated when the `slice` stage is executed with the following output:
```bash
'titanic.csv.dvc' didn't change, skipping
Running stage 'slice' with command:
	python slice-data.py
Updating lock file 'dvc.lock'

To track the changes with git, run:

	git add dvc.lock
```
