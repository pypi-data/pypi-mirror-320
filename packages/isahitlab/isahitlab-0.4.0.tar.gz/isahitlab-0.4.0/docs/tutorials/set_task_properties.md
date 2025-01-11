# Task properties update

You can add set some properties on your tasks.

!!! info "Code Reference"
    See the [code reference](../../task/#isahitlab.actions.task.TaskActions.update_properties_of_tasks) for further details.

## Available properties


| Property    | Type        |
| ----------- | ----------- |
| score       | *number*    |



## Example


```python
from isahitlab.client import IsahitLab

lab = IsahitLab()

lab.update_properties_of_tasks(
    project_id='<project_id>',
    task_id_in=['<task_id>'],
    properties={ "score" : 5 }
)
```


!!! neutral "Remove properties"
    Set the property to `None` to remove it