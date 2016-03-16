# Logstash

## Input

    pipe { command => "/opt/journald-stream" codec => "json"}
    
ENV

* JOURNAL_DIRECTORY
* JOURNAL_DEBUG
