Im Dockerfile sind die requirements enthalten.

In ../WebApp wechseln über das Terminal/CMD

1. Image in Docker erstellen:
            docker build -t sema/webapp .
            
            
2. Image ausführen und den Port 8000 über den Port 8002 erreichen:
            docker run -p 8002:8000 sema/webapp
