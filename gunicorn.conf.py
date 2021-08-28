import multiprocessing

bind = "127.0.0.1:9001"
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100
workers = 4
timeout = 6000

keyfile = "privkey.pem"
certfile = "cert.pem"
ca_certs = "chain.pem"