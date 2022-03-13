package ngo

import (
	"context"
	"time"

	"github.com/fabioberger/airtable-go"

	"github.com/ngo-coordination-warsaw/ngo-api/internal/pkg/types"
)

const airtableTTL = time.Second * 10

type ngo struct {
	config   types.Config
	ctx      context.Context
	airtable *airtable.Client

	organizationsData map[string][]org
	adminsData        map[string]struct{}
	categoriesData    []interface{}
}

func NewNgo(ctx context.Context, cfg types.Config) (*ngo, error) {
	a, err := airtable.New(cfg.AirtableApiKey, cfg.AirtableBaseID)
	if err != nil {
		return nil, err
	}

	return &ngo{
		config:   cfg,
		ctx:      ctx,
		airtable: a,

		organizationsData: make(map[string][]org),
	}, nil
}

func (ngo *ngo) LoadAirtable() error {
	ngo.loadAirtable()

	for {
		select {
		case <-ngo.ctx.Done():
			break
		case <-time.After(airtableTTL):
			ngo.loadAirtable()
		}
	}

	return nil
}
