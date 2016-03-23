# Logstash

## Input

    pipe { command => "/opt/journald-stream" }
    
    
## ENV

By default a define set this to "/run/log/journal", override with:
    
    JOURNAL_DIRECTORY || --directory=
 

For debug program:

    JOURNAL_DEBUG=true
