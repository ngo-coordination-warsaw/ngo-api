package utils

import (
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

func GracefulStop(waitGroup *sync.WaitGroup, waitTimeout time.Duration, stopFunc func()) {
	var gracefulStop = make(chan os.Signal)
	signal.Notify(gracefulStop, syscall.SIGTERM, syscall.SIGINT)
	<-gracefulStop

	// Run
	stopFunc()

	if waitGroup != nil {
		closeChan := make(chan struct{})

		go func() {
			defer close(closeChan)
			waitGroup.Wait()
		}()

		select {
		case <-closeChan:
			log.Info("Service stopped")
		case <-time.After(waitTimeout):
			log.Warnf("Service stopped after timeout")
		}
	}
}
