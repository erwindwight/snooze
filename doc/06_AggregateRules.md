# Aggregate Rules

![Architecture](images/architecture.png)

## Overview

Group Records based on matching fields and a throttle period.

Records have to match the Aggregate's condition in order to being processed.

Aggregates are mainly designed to prevent similar Records from being notified especially if they were sent in burst or the process generating them was flapping.

For example:
```yaml
# Record A
host: prod-syslog01.example.com
process: sssd[2564]
message: Preauthentication failed
timestamp: 2021-01-01 10:00:00

# Record B
host: prod-syslog01.example.com
process: sssd[2566]
message: Preauthentication failed
timestamp: 2021-01-01 10:10:00

# Record C
host: prod-syslog01.example.com
process: sssd[2569]
message: Preauthentication failed
timestamp: 2021-01-01 10:20:00
```
```yaml
# Aggregate
fields:
    - host
    - message
throttle: 900 # 15 mins
```
All three Records have the same fields `host` and `message`. 

Record A being the first one processed, it was correctly passed to the next Process plugin. The throttle period started from Record A timestamp.

Record B was processed 10 minutes after Record A which was lower than the throttle period (15 mins), therefore Record B was not passed to the next Process plugin.

Record C was processed 20 minutes after Record A which was greater than the throttle period, therefore Record C was correctly passed to the next Process plugin. The throttle period restarted from Record C timestamp.

**Note**: On the web interface, it is possible to see how many times a Record was aggregated by checking the number on the very right in **Aggregates** section:

![Aggregates](images/web_aggregates.png)

## Web interface ##

![Aggregate Rules](images/web_aggregaterules.png)

* `Name`*: Name of the aggregate rule.
* `Condition`: This aggregate rule will be triggered only if this condition is matched. Leave it blank to always match.
* `Fields`: Space separated values used to group incoming alerts.
* `Throttle`: Number of seconds to wait before escalating the next alert matching this aggregate rule (-1 for infinite).
* `Comment`: Description.
