import threading


class CaptureMixin:
    def start_capture(self):
        try:
            threading.Thread(
                target=self.Capture.start_capture,
                args=(self.params,),
                name="CaptureThread",
                daemon=True,
            ).start()
        except Exception as e:
            self.logger.LogExit("start_capture", e)
            self.running = False
