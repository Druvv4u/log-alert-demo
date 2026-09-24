import json
import logging
from flask import Flask

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "demo-app"
        })

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler("/var/log/app/app.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

app = Flask(__name__)

@app.route("/health")
def health():
    logger.info("Health check passed")
    return {"status": "ok"}

@app.route("/crash")
def crash():
    logger.error("About to hit a real unhandled exception")
    data = {"user": "abhay"}
    return data["email"]  # this key doesn't exist -> real KeyError

if __name__ == "__main__":
    logger.info("App starting up")
    app.run(host="0.0.0.0", port=8080)
