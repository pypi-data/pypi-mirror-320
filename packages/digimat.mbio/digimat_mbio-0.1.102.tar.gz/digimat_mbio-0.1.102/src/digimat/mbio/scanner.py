#!/bin/python

from .task import MBIOTask
from .xmlconfig import XMLConfig


class MBIOTaskScanner(MBIOTask):
    def initName(self):
        return 'scanner'

    def onInit(self):
        self.config.set('refresh', 0)
        self.config.set('threads', 32)
        self.config.set('network', self.getMBIO().network)
        self._scan=False
        self._sio=False
        self._tokenSIO=None
        self._mc=False
        # Wait some time before launching first scan after start
        self._timeoutRefresh=self.timeout(15)

    def onLoad(self, xml: XMLConfig):
        self.config.update('refresh', xml.getInt('refresh', vmin=60))
        self.config.update('threads', xml.getInt('threads', vmax=64))
        self.config.update('network', xml.get('network'))

        item=xml.child('sio')
        if item is not None:
            self._tokenSIO=item.get('token')
            self._sio=True

        item=xml.child('mcx')
        if item is not None:
            self._mc=True

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def scanSIO(self):
        try:
            from .digimatsmartio import SIOScanner
            s=SIOScanner(self.getMBIO(),
                         network=self.config.network,
                         maxthreads=self.config.threads)
            s.setToken(self._tokenSIO)
            s.configureNetwork()
        except:
            pass

    def scanMC(self):
        try:
            from .metzconnect import MCScanner
            s=MCScanner(self.getMBIO(),
                        network=self.config.network,
                        maxthreads=self.config.threads)
            s.configureNetwork()
        except:
            pass

    def run(self):
        if self.isTimeout(self._timeoutRefresh):
            period=self.config.getInt('refresh')
            if not self._scan or period>0:
                self.logger.info('%s: Launching scan (network=%s, maxthreads=%d)...' %
                                 (self.__class__.__name__,
                                  self.config.network, self.config.threads))
                if self._sio:
                    self.logger.debug('%s: Starting SIO scan...' % (self.__class__.__name__))
                    self.scanSIO()
                    self.logger.debug('%s: SIO scan done' % (self.__class__.__name__))

                if self._mc:
                    self.logger.debug('%s: Starting MetzConnect scan...' % (self.__class__.__name__))
                    self.scanMC()
                    self.logger.debug('%s: MetzConnect scan done' % (self.__class__.__name__))

                self.logger.debug('%s: Scan done' % (self.__class__.__name__))

                self._timeoutRefresh=self.timeout(max(60, period))
                self._scan=True

        return 15.0


if __name__ == "__main__":
    pass
