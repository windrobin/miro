import unittest

import database
import eventloop
import frontend
import app
import downloader

class HadToStopEventLoop(Exception):
    pass

class DemocracyTestCase(unittest.TestCase):
    def setUp(self):
        # reset the event loop
        database.resetDefaultDatabase()
        eventloop._eventLoop.threadPool.closeThreads()
        eventloop._eventLoop = eventloop.EventLoop() 

    def tearDown(self):
        # this prevents weird errors when we quit
        eventloop._eventLoop.threadPool.closeThreads()


class EventLoopTest(DemocracyTestCase):
    def setUp(self):
        DemocracyTestCase.setUp(self)
        self.hadToStopEventLoop = False

    def stopEventLoop(self):
        self.hadToStopEventLoop = True
        eventloop.quit()

    def runPendingIdles(self):
        idleQueue = eventloop._eventLoop.idleQueue
        urgentQueue = eventloop._eventLoop.urgentQueue
        while idleQueue.hasPendingIdle() or urgentQueue.hasPendingIdle():
            urgentQueue.processIdles()
            idleQueue.processNextIdle()

    def runEventLoop(self, timeout=10, timeoutNormal=False):
        self.hadToStopEventLoop = False
        timeout = eventloop.addTimeout(timeout, self.stopEventLoop, 
                "Stop test event loop")
        eventloop._eventLoop.quitFlag = False
        eventloop._eventLoop.loop()
        if self.hadToStopEventLoop and not timeoutNormal:
            raise HadToStopEventLoop()
        else:
            timeout.cancel()

    def processIdles(self):
        eventloop._eventLoop.idleQueue.processIdles()
        eventloop._eventLoop.urgentQueue.processIdles()

class DownloaderTestCase(EventLoopTest):
    def setUp(self):
        DemocracyTestCase.setUp(self)
        # FIXME: This is kind of ugly
        app.delegate = frontend.UIBackendDelegate()
        downloader.startupDownloader()

    def tearDown(self):
        DemocracyTestCase.tearDown(self)
        downloader.shutdownDownloader(eventloop.quit)
        self.runEventLoop()
        app.delegate = None
