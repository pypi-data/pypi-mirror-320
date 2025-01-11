from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from pydantic import BaseModel
from io import BytesIO
import base64
from PIL import Image
from escpos.escpos import EscposIO
from escpos.printer import Network

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrintRequest(BaseModel):
    printer_ip: str
    port: int = 9100
    data: str

class PrinterAPI:
    def __init__(self, printer_ip: str, port: int, data: str):
        self.printer_ip = printer_ip
        self.port = port
        self.data = data

    def process_image_and_print(self):
        try:
            # Decode and load the image
            image_io = BytesIO(base64.b64decode(self.data))
            image = Image.open(image_io)

            # Send the image to the printer
            printer = Network(self.printer_ip, port=self.port)
            with EscposIO(printer, autocut=True) as p:
                p.printer.image(image)

            return self._success_response()
        except Exception as e:
            return self._error_response(str(e))

    def _success_response(self):
        return JSONResponse({"status": "success"}, status_code=status.HTTP_200_OK)

    def _error_response(self, error_message: str):
        return JSONResponse({"status": "error", "message": error_message}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post('/print')
async def print_receipt(print_request: PrintRequest):
    try:
        printer_api = PrinterAPI(print_request.printer_ip, print_request.port, print_request.data)
        return printer_api.process_image_and_print()

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=8100, 
        ssl_certfile="./ssl/certificate.crt",
        ssl_keyfile="./ssl/private.key",
        ssl_ca_certs="./ssl/ca_bundle.crt" 
    )