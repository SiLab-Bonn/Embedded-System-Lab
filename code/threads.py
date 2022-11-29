import threading
import time

class TestThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running=True
        self.start()

    def run(self):        
        while self.running:
            time.sleep(0.5)
            print("running")

    def stop(self):
        self.running=False

if __name__=='__main__':

    tt=TestThread()
    a=input('simple stuff working ? -- ')
    tt.stop()