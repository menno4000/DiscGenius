import multiprocessing

bind = "0.0.0.0:443"
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 100
workers = 4
timeout = 6000

keyfile = "privkey.pem"
certfile = "cert.pem"
ca_certs = "chain.pem"