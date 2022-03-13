package main

import (
	"context"
	"flag"
	"github.com/ngo-coordination-warsaw/ngo-api/internal/ngo"
	"github.com/ngo-coordination-warsaw/ngo-api/internal/pkg/types"
	"github.com/ngo-coordination-warsaw/ngo-api/internal/pkg/utils"
	"sync"
	"time"

	log "github.com/sirupsen/logrus"
)

const (
	waitTimeout = time.Second * 10
)

func main() {
	var wg sync.WaitGroup

	var flags struct {
		logLevel string
		envFile  string
	}

	flag.StringVar(&flags.logLevel, "log", "debug", "log level [debug|info|warn|error|crit]")
	flag.StringVar(&flags.envFile, "env", "", "path to environment file")
	flag.Parse()

	// Set logging level
	lvl, err := log.ParseLevel(flags.logLevel)
	if err != nil {
		log.Fatalf("ParseLogLevel: %s", err.Error())
	}

	log.SetLevel(lvl)

	var cfg types.Config
	err = types.InitConfig(&cfg, flags.envFile)
	if err != nil {
		log.Fatalf("ParseLogLevel: %s", err.Error())
	}

	ctx, ctxCancel := context.WithCancel(context.Background())

	ctrl, err := ngo.NewNgo(ctx, cfg)
	if err != nil {
		log.Fatalf("NewNgo: %s", err.Error())
	}

	go func() {
		if err := ctrl.ServeAPI(); err != nil {
			log.Fatalf("ServeAPI: %s", err.Error())
		}
	}()

	go func() {
		if err := ctrl.LoadAirtable(); err != nil {
			log.Errorf("LoadAirtable: %s", err.Error())
		}
	}()

	utils.GracefulStop(&wg, waitTimeout, func() {
		ctxCancel()
	})
}
