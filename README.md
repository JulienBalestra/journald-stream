# Logstash

## Input

    pipe { command => "/opt/journald-stream" }
    
    
## ENV


### Journal directory

By default a define set this to "/run/log/journal", override with:
    
    JOURNAL_DIRECTORY || --directory=

### SinceDB

For custom sincedb path:

    SINCE_DB_PATH=/var/lib/logstash/sincedb
    
Otherwise the sincedb file will be created inside the current working directory.
 
### Debug

For debug program:

    JOURNAL_DEBUG=true

## Samples

    [Service]
    ExecStartPre=/usr/bin/docker pull logstash
    ExecStartPre=-/usr/bin/docker kill logstash
    ExecStart=/usr/bin/docker run --rm \
      -v /opt/journald-stream.d/journald-stream:/opt/journald-stream:ro \
      -v /run/log/journal:/run/log/journal:ro \
      -v /opt/journald-stream.d/logstash.conf:/etc/logstash.conf:ro \
      -v /var/lib/logstash/sincedb:/var/lib/logstash/sincedb:rw \
      -e SINCE_DB_PATH=/var/lib/logstash/sincedb \
      logstash \
      /bin/bash -c 'logstash -f /etc/logstash.conf'
    ExecStop=/usr/bin/docker stop logstash

/etc/logstash.conf:


    input {
            pipe { command => "/opt/journald-stream" }
          }
    output {
            elasticsearch { hosts => elasticsearch:9200" }
          }