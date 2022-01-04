## Parsing data and create HTML files

*Requirements:* [Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).

1. Create conda environment importing the ```yashiro_env.yml```
2. Activate the env and run ```python script.py -f [letters] [people] [images] ```

You can find the output files in `[directory]/data`, where directory can be `letters`, `people`, `images`.

## Upload extracted data online

*Requirements:* Local running [ResearchSpace](https://researchspace.org) instance.

To run create the following file called `.env` in the root directory and update username/password

```
{
    "user": "xxx",
    "pasw": "xxx"    
}
```

Run the script adding the flag -u, it will automatically upload all the named graphs on the local running ResearchSpace instance. 

TODO: the graph API URI shoudl be defined at runtime.
