import cv2
from operations.databaseOperations import DatabaseOperations
from ultralytics import YOLO
from operations.mailProvider import MailProvider
import time
from operations.botProvider import BotProvider

class VideoWorker:
    def setup(self, authenticationId):
         self.sent_request = False
         self.databaseOperations = DatabaseOperations()
         self.model = YOLO('.\\models\\best.pt')
         self.mailProvider = MailProvider()
         self.accident_timestamps = {}
         self.start_time = None
         self.location = None
         self.authenticationId = authenticationId
         self.botProvider = BotProvider()

    def accident_detected_callback(self, image, result, location):
        current_time = time.time()

        if location in self.accident_timestamps:
            if current_time - self.accident_timestamps[location] >= 10:
                self.accident_timestamps[location] = current_time
                self.sent_request = False
            else:
                 self.sent_request = True
        else:
            self.accident_timestamps[location] = current_time

        detections = result.boxes.cls
        accident_boxes = result.boxes[detections != 0]
        for box in accident_boxes:
                self.start_time = time.time()
                for xyxy in box.xyxy:
                    if self.sent_request == False:
                        _, image_bytes = cv2.imencode('.jpg', image)
                        self.location = location

                        prefferedMethod = self.databaseOperations.getPrefferedInformationMethod(self.authenticationId)

                        if prefferedMethod == 0 or prefferedMethod == 2:
                            self.mailProvider.send_email(f"{result.names[int(box.cls)]} {float(box.conf)}", f"Accident detected on {location}", image, self.getTimeCallBack)
                        if prefferedMethod == 1 or prefferedMethod == 2:
                            chat_id = self.databaseOperations.getChatIdByAuthenticationId(self.authenticationId)
                            self.botProvider.informUserAboutInsident(chat_id, f"Accident detected on {location} with confidence: {float(box.conf)}", image_bytes)
                            self.getTimeCallBack(time.time(), 1)

                        self.databaseOperations.insertNewAccident(location, result.names[int(box.cls)], image_bytes, box.conf)
                        self.sent_request = True

        return image
    
    def getTimeCallBack(self, endTime, sendBy):
        self.databaseOperations.insertTimeForAccidentReport(self.location, endTime - self.start_time, sendBy)
    
    def detectAccidents(self, frame, location):
        results = self.model.predict(frame, show=False, stream=True, classes=[1, 2], conf=0.5)
        first_result = next(results)
        return self.accident_detected_callback(first_result.plot(), first_result, location)