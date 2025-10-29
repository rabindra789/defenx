```bash 
sudo cat /etc/systemd/system/defenx.service
```

```service

[Unit]
Description=DefenX Port Scanner & Health Monitor
After=network.target

[Service]
Type=simple
User=ubuntu 
WorkingDirectory=/home/ubuntu/defenx 
ExecStart=/home/ubuntu/defenx/env/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
Restart=always 
RestartSec=5 
StandardOutput=append:/home/ubuntu/defenx/defenx.log
StandardError=append:/home/ubuntu/defenx/defenx.err 

[Install] 
WantedBy=multi-user.target
```